# coding:utf-8

import sys
from mantis.fundamental.application.use_gevent import USE_GEVENT

if USE_GEVENT:
    from gevent.queue import Queue
else:
    from Queue import Queue

import json
from threading import Thread
from collections import OrderedDict
from optparse import OptionParser

from vnpy.event import EventEngine
from vnpy.trader.vtEvent import EVENT_LOG, EVENT_ERROR, EVENT_TICK, EVENT_CONTRACT
from vnpy.trader.vtEngine import MainEngine
from vnpy.trader.gateway import ctpGateway,xtpGateway
from vnpy.trader.vtObject import *
from vnpy.trader.vtObject import VtSubscribeReq
from mantis.fundamental.application.app import instance
from mantis.fundamental.utils.useful import hash_object
from mantis.trade.service import TradeService, TradeFrontServiceTraits, ServiceType
from mantis.trade.constants import *
from mantis.trade.types import *
from mantis.trade.message import *
from mantis.trade import command
from dataslot import DataEngine


class TradeAdapter(TradeService, TradeFrontServiceTraits):
    def __init__(self, name):
        TradeService.__init__(self, name)
        TradeFrontServiceTraits.__init__(self)

        self.active = False  # 工作状态
        self.queue = Queue()  # 队列
        self.thread = Thread()  # 线程
        self.ee = None
        self.mainEngine = None
        self.dataEngine = None
        self.logger = instance.getLogger()
        self.symbols = {}  # 已经订阅的合约
        self.contracts = OrderedDict()

        self.runMode = StrategyRunMode.Product  # 产品模式还是开发模式 trade - 产品 ; development - 交易
        self.product = ''
        self.account = ''

        self.down_counter = 0  # 继续运行标志

    def init(self, cfgs, **kwargs):
        self.parseOptions()
        super(TradeAdapter, self).init(cfgs)


    def initCommandChannels(self):
        TradeService.initCommandChannels(self)

    def handle_channel_sub(self,data,ctx):
        message = Message.unmarshall(data)
        if not message:
            return
        if message.name == command.KeepAlive.NAME:
            # 处理保活，系统不应该退出
            self.keepAlive()

    def processOrderRequest(self,order):
        """处理下单请求 , 走 http 通道"""
        pass

    def parseOptions(self):

        parser = OptionParser()
        parser.add_option("--product", dest='product',help=u'futures / stock')
        parser.add_option("--account", dest='account',help=u' account')
        parser.add_option("--mode",default=StrategyRunMode.Product, dest='mode',help=u'dev/product')

        args = sys.argv[1:]
        (options, args) = parser.parse_args(args)

        # 产品和账号必须提供
        if not options.product or not options.account:
            instance.abort()
            return

        # 产品类型检查
        if options.product not in ( ProductClass.Future,ProductClass.Stock):
            print 'Error: Option [ --product ] Must Be ({},{})'.format(ProductClass.Stock,ProductClass.Future)
            instance.abort()
            return

        self.service_id = TradeAdapterServiceIdFormat.format(product=options.product,account=options.account)
        self.service_type = ServiceType.TradeAdapter
        self.product = options.product
        self.account = options.account

    def  getTradeAccountDetail(self):
        """查询账号配置细节，包括：登录用户名、密码、服务器信息等"""

        if self.runMode == StrategyRunMode.Product:
            key = TradeAccountNameFormat
        else:
            key = DevelopAccountNameFormat
        key = key.format(product=self.product,account=self.account)
        conn = instance.datasourceManager.get('redis').conn
        return conn.hgetall(key)

    def syncDownServiceConfig(self):
        TradeService.syncDownServiceConfig(self)

    def keepAlive(self):
        self.down_counter = TimeDuration.MINUTE_5 * 100000

    def timerKeepAliveCheck(self,timer):
        """"""
        self.down_counter -= timer.timeout
        if self.down_counter <= 0:
            print 'Info: Service Adapter is UnNeeded, Stop it..'
            instance.stop()

    def setupFanoutAndLogHandler(self):
        from mantis.trade.log import TradeServiceLogHandler
        self.initFanoutSwitchers(self.cfgs.get('fanout'))
        handler = TradeServiceLogHandler(self)
        self.logger.addHandler(handler)

    def start(self, block=True):
        # return
        self.setupFanoutAndLogHandler()
        # 创建日志引擎
        TradeService.start(self)

        self.keepAlive()
        self.registerTimedTask(self.timerKeepAliveCheck)

        self.active = True
        self.thread.start()

        le = self.logger
        le.info(u'启动行情记录运行子进程')

        cfgs = self.getTradeAccountDetail()

        self.ee = EventEngine()
        le.info(u'事件引擎创建成功')
        self.dataEngine = DataEngine(self.ee,self)
        self.mainEngine = MainEngine(self.ee,self.dataEngine)  # 忽略掉 默认的 DataEngine

        gatewayName = ''
        if self.product == ProductClass.Future:
            self.mainEngine.addGateway(ctpGateway)
            gatewayName = ctpGateway.gatewayName

        if self.product == ProductClass.Stock:
            self.mainEngine.addGateway(xtpGateway)
            gatewayName = xtpGateway.gatewayName

        le.info(u'主引擎创建成功')
        le.info(u'注册日志事件监听')
        self.registerEvent()
        self.mainEngine.connect(gatewayName, cfgs)

        le.info(u'连接CTP接口')

    def processLogEvent(self, event):
        print self,event

    def processErrorEvent(self, event):
        """
        处理错误事件
        错误信息在每次登陆后，会将当日所有已产生的均推送一遍，所以不适合写入日志
        """
        error = event.dict_['data']
        print u'错误代码：%s，错误信息：%s' % (error.errorID, error.errorMsg), self

    def stop(self):
        TradeService.stop(self)
        self.mainEngine.exit()
        if self.active:
            self.active = False
            # self.thread.join()

    def join(self):
        self.thread.join()

    def registerEvent(self):
        """注册事件监听"""

        self.ee.register(EVENT_LOG, self.processLogEvent)
        self.ee.register(EVENT_ERROR, self.processErrorEvent)

    def publishMessage(self,data):
        """
        通过pub通道将消息发布给策略runner
        :param data:  VtTradeData and VtOrderData
        :return:
        """
        message = None
        channel = self.channels.get('pub') #
        if isinstance(data,VtTradeData):
            message = Message(command.OnTradeData.NAME)
        if isinstance(data,command.OnOrderData.NAME):
            message = Message(command.OnOrderData.NAME)

        if message:
            message.data = data.__dict__
            Request(channel).send(message)
