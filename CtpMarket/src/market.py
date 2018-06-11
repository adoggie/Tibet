# coding:utf-8

from mantis.fundamental.application.use_gevent import USE_GEVENT
if USE_GEVENT:
    from gevent.queue import Queue
else:
    from queue import Queue

import json
from threading import Thread
from datetime import datetime, time
from collections import OrderedDict

from vnpy.event import EventEngine
from vnpy.trader.vtEvent import EVENT_LOG, EVENT_ERROR,EVENT_TICK,EVENT_CONTRACT
from vnpy.trader.vtEngine import MainEngine, LogEngine
from vnpy.trader.gateway import ctpGateway
from vnpy.trader.vtObject import VtSubscribeReq, VtLogData, VtBarData, VtTickData
from mantis.fundamental.application.app import instance
from mantis.fundamental.utils.useful import hash_object
from mantis.trade.service import TradeService,TradeFrontServiceTraits,ServiceType,ServiceCommonProperty

class MarketService(TradeService,TradeFrontServiceTraits):
    def __init__(self,name):
        TradeService.__init__(self,name)
        TradeFrontServiceTraits.__init__(self)

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

    def init(self, cfgs,**kwargs):
        self.service_id = cfgs.get('id')
        self.service_type = ServiceType.MarketAdapter
        super(MarketService,self).init(cfgs)


    def syncDownServiceConfig(self):
        TradeService.syncDownServiceConfig(self)
        TradeFrontServiceTraits.syncDownServiceConfig(self)

        cfg_gateway = self.cfgs.get('gateway')
        self.product_class = 'FUTURES' #self.cfgs_remote.get(ServicePropertyFrontService.ProductClass.v)
        self.exchange = cfg_gateway.get('name')
        self.gateway = cfg_gateway.get('name')
        self.broker = cfg_gateway.get('brokerID')
        self.user = cfg_gateway.get('userID')
        self.password = cfg_gateway.get('password')
        self.market_server_addr = cfg_gateway.get('mdAddress')
        self.trade_server_addr = cfg_gateway.get('tdAddress')
        self.auth_code = cfg_gateway.get('authCode')
        self.user_product_info = cfg_gateway.get('userProductInfo')

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
        self.mainEngine.addGateway(ctpGateway)
        le.info(u'主引擎创建成功')



        le.info(u'注册日志事件监听')

        self.registerEvent()
        # cfgs = self.cfgs.get('gateway',{}) # 本地加载
        cfgs = self.convertToVnpyGatewayConfig()
        self.mainEngine.connect( self.gateway,cfgs)

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
                self.mainEngine.subscribe(req, self.gateway) # CTP
                self.symbols[symbol] = symbol


    def unsubscribe(self,*symbols):
        for s in symbols:
            if s in self.symbols.keys():
               del  self.symbols[s]

    def getSymbols(self):
        return list(self.contracts.keys())


    def procecssTickEvent(self, event):
        """处理行情事件"""
        tick = event.dict_['data']

        # 生成datetime对象
        if not tick.datetime:
            # tick.datetime = datetime.strptime(' '.join([tick.date, tick.time]), '%Y%m%d %H:%M:%S.%f')
            tick.service = self.getServiceType() +'.'+self.getServiceId()
        self.queue.put(tick)


    def registerEvent(self):
        """注册事件监听"""
        self.ee.register(EVENT_TICK, self.procecssTickEvent)
        self.ee.register(EVENT_LOG, self.processLogEvent)
        self.ee.register(EVENT_ERROR, self.processErrorEvent)
        self.ee.register(EVENT_CONTRACT, self.processContractEvent)

    def subscribeAllContracts(self):
        for symbol in self.contracts.keys():
            req = VtSubscribeReq()
            req.symbol = symbol
            self.mainEngine.subscribe(req, self.gateway)  # CTP

    def processContractEvent(self, event):
        """处理合约事件
           连接交易系统之后,会通过此接口接收到CTP所有当前合约
        """
        contract = event.dict_['data']
        self.contracts[ contract.vtSymbol] = contract
        if contract.last:
            # start contract subscribe
            self.subscribeAllContracts()


    def threadDataFanout(self):
        """运行插入线程"""
        while self.active:
            try:
                # print 'current tick queue size:', self.queue.qsize()
                # dbName, collectionName, d = self.queue.get(block=True, timeout=1)
                tick  = self.queue.get(block=True, timeout=1)
                symbol = tick.vtSymbol
                hashobj =  hash_object(tick)
                jsondata = json.dumps(hashobj)
                self.dataFanout('switch0',jsondata,symbol = symbol)
                self.ticks_counter += 1
                if len(self.ticks_samples) > 5:
                    del self.ticks_samples[0]
                self.ticks_samples.append(hashobj)

            except Exception as e:
                # self.logger.error( str(e) )
                pass
