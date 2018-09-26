# coding:utf-8

from mantis.fundamental.application.use_gevent import USE_GEVENT
if USE_GEVENT:
    from gevent.queue import Queue
else:
    from Queue import Queue

import json
import datetime,time
from threading import Thread
from datetime import datetime, time
from collections import OrderedDict

from vnpy.event import EventEngine
from vnpy.trader.vtEvent import EVENT_LOG, EVENT_ERROR,EVENT_TICK,EVENT_CONTRACT
from vnpy.trader.vtEngine import MainEngine, LogEngine
from vnpy.trader.gateway import xtpGateway
from vnpy.trader.vtConstant import *
from vnpy.trader.vtObject import VtSubscribeReq, VtLogData, VtBarData, VtTickData
from mantis.fundamental.application.app import instance
from mantis.fundamental.utils.timeutils import datetime_to_timestamp
from mantis.trade.service import TradeService,ServiceType,ServiceCommonProperty
from mantis.trade.constants import *



class MarketService(TradeService):
    def __init__(self,name):
        TradeService.__init__(self,name)

        self.active = False  # 工作状态
        self.queue = Queue()  # 队列
        self.thread = Thread(target=self.threadDataFanout)  # 线程
        self.ee = None
        self.mainEngine = None
        self.logger = instance.getLogger()
        self.symbols = {} # 已经订阅的合约
        self.contracts = OrderedDict()
        self.ticks_counter = 0
        self.ticks_samples = []
        self.tick_filters =[]

    def init(self, cfgs,**kwargs):
        self.service_id = cfgs.get('id')
        self.service_type = ServiceType.MarketAdapter
        super(MarketService,self).init(cfgs)
        self.initFilters()


    def syncDownServiceConfig(self):
        TradeService.syncDownServiceConfig(self)

    def setupFanoutAndLogHandler(self):
        from mantis.trade.log import TradeServiceLogHandler
        self.initFanoutSwitchers(self.cfgs.get('fanout'))

        handler = TradeServiceLogHandler(self)
        self.logger.addHandler(handler)

    def start(self,block=True):
        self.setupFanoutAndLogHandler()

        # 创建日志引擎
        super(MarketService,self).start()
        self.active = True
        self.thread.start()

        le = self.logger
        # le = LogEngine()
        # le.setLogLevel(le.LEVEL_INFO)
        # le.addConsoleHandler()
        le.info(u'启动行情记录运行子进程')

        self.ee = EventEngine()
        le.info(u'事件引擎创建成功')

        self.mainEngine = MainEngine( self.ee) # 忽略掉 默认的 DataEngine
        self.mainEngine.addGateway(xtpGateway)
        le.info(u'主引擎创建成功')

        le.info(u'注册日志事件监听')

        self.registerEvent()
        cfgs = self.cfgs.get('gateway', {})
        self.mainEngine.connect(xtpGateway.gatewayName,cfgs)

        le.info(u'连接CTP接口')



    def processLogEvent(self,event):
        print event

    def processErrorEvent(self,event):
        """
        处理错误事件
        错误信息在每次登陆后，会将当日所有已产生的均推送一遍，所以不适合写入日志
        """
        error = event.dict_['data']
        print u'错误代码：%s，错误信息：%s' % (error.errorID, error.errorMsg)

    def stop(self):
        super(MarketService,self).stop()
        self.mainEngine.exit()
        if self.active:
            self.active = False
            # self.thread.join()

    def join(self):
        self.thread.join()


    def subscribe(self,*symbols):
        for symbol in symbols:
            if not self.symbols.has_key(symbol):
                req = VtSubscribeReq()
                req.symbol = symbol
                self.mainEngine.subscribe(req, xtpGateway.gatewayName) # XTP
                self.symbols[symbol] = symbol

        if not symbols :
            self.mainEngine.subscribe(None,xtpGateway.gatewayName) # 订阅全市场所有股票

    def unsubscribe(self,*symbols):
        for s in symbols:
            if s in self.symbols.keys():
               del  self.symbols[s]

    def getSymbols(self):
        return list(self.contracts.keys())

    def procecssTickEvent(self, event):
        """处理行情事件"""
        tick = event.dict_['data']
        tick = self.filterTicks(tick)
        # print 'Tick:',tick
        if tick:
            # 生成datetime对象
            if not tick.datetime:
                # tick.datetime = datetime.strptime(' '.join([tick.date, tick.time]), '%Y%m%d %H:%M:%S.%f')
                tick.service = self.getServiceType() +'.'+self.getServiceId()
            self.queue.put(tick)

    def initFilters(self):
        from mantis.fundamental.utils.importutils import import_class
        for clsname in self.cfgs.get('xtp_tick_filters',[]):
            cls = import_class(clsname)
            filter = cls()
            self.tick_filters.append(filter)

    def filterTicks(self,tick):
        """必须同时满足所有filter数据检查条件"""
        for f in self.tick_filters:
            tick = f.validate(tick)
            if not tick:
                break
        return tick

    def registerEvent(self):
        """注册事件监听"""
        self.ee.register(EVENT_TICK, self.procecssTickEvent)
        self.ee.register(EVENT_LOG, self.processLogEvent)
        self.ee.register(EVENT_ERROR, self.processErrorEvent)
        self.ee.register(EVENT_CONTRACT, self.processContractEvent)

    # def subscribeAllContracts(self):
    #     self.subscribeSymobls()
    #     return
    #     for symbol in self.contracts.keys():
    #         req = VtSubscribeReq()
    #         req.symbol = symbol
    #         req.exchange = EXCHANGE_SSE
    #         # self.mainEngine.subscribe( req, xtpGateway.gatewayName)  # CTP
    #     self.mainEngine.subscribe( None, xtpGateway.gatewayName)  # CTP

    def subscribeSymobls(self):
        import string
        symbols =  map(string.strip,self.cfgs.get('sub_symbols','').split(','))
        for symbol in symbols:
            req = VtSubscribeReq()
            req.symbol = symbol
            req.exchange = EXCHANGE_SSE
            self.mainEngine.subscribe( req, xtpGateway.gatewayName)  #


    def processContractEvent(self, event):
        """处理合约事件
           连接交易系统之后,会通过此接口接收到CTP所有当前合约
        """
        contract = event.dict_['data']
        self.contracts[ contract.vtSymbol] = contract
        if contract.last:
            # start contract subscribe
            self.subscribeSymobls()


    def threadDataFanout(self):
        """运行插入线程"""
        while self.active:
            try:
                # print 'current tick queue size:', self.queue.qsize()
                # dbName, collectionName, d = self.queue.get(block=True, timeout=1)
                tick  = self.queue.get(block=True, timeout=1)
                symbol = tick.vtSymbol

                dt = datetime.datetime.strptime(' '.join([tick.date, tick.time]), '%Y%m%d %H:%M:%S.%f')
                tick.ts = datetime_to_timestamp(dt)  # 合约生成时间
                tick.ts_host = int(time.time())  # 主机系统时间

                jsondata = json.dumps(tick.__dict__)
                self.dataFanout('switch0',jsondata,symbol = symbol)

                # -- cache current tick into redis ---
                key_name = XtpMarketSymbolTickFormat.format(symbol=tick.vtSymbol)
                redis = instance.datasourceManager.get('redis').conn
                redis.hmset(key_name, tick.__dict__)

                print 'Tick:',tick.__dict__
                self.ticks_counter += 1
                if len(self.ticks_samples) > 5:
                    del self.ticks_samples[0]
                self.ticks_samples.append(tick.__dict__)

            except Exception as e:
                # self.logger.error( str(e) )
                pass
