# coding:utf-8

from gevent.queue import Queue
from threading import Thread
from datetime import datetime, time

from vnpy.event import EventEngine2
from vnpy.trader.vtEvent import EVENT_LOG, EVENT_ERROR,EVENT_TICK
from vnpy.trader.vtEngine import MainEngine, LogEngine
from vnpy.trader.gateway import ctpGateway
from vnpy.trader.vtObject import VtSubscribeReq, VtLogData, VtBarData, VtTickData
from mantis.fundamental.application.app import instance

from mantis.fundamental.service import ServiceBase
from mantis.trade.service import TradeService,TradeFrontServiceTraits

class MarketService(TradeService,TradeFrontServiceTraits):
    def __init__(self,name):
        super(TradeService, self).__init__(name)
        super(TradeFrontServiceTraits,self).__init__()

        self.active = False  # 工作状态
        self.queue = Queue()  # 队列
        self.thread = Thread(target=self._run)  # 线程
        self.ee = None
        self.mainEngine = None
        self.logger = instance.getLogger()
        self.symbols = set() # 已经订阅的合约

    def init(self, cfgs):
        super(MarketService,self).init(cfgs)

    def syncDownServiceConfig(self):
        TradeService.syncDownServiceConfig(self)
        TradeFrontServiceTraits.syncDownServiceConfig(self)


    def start(self,block):
        # 创建日志引擎
        super(MarketService,self).start()
        self.active = True
        self.thread.start()

        le = self.logger
        # le = LogEngine()
        # le.setLogLevel(le.LEVEL_INFO)
        # le.addConsoleHandler()
        le.info(u'启动行情记录运行子进程')

        self.ee = EventEngine2()
        le.info(u'事件引擎创建成功')

        self.mainEngine = MainEngine( self.ee,self) # 忽略掉 默认的 DataEngine
        self.mainEngine.addGateway(ctpGateway)
        le.info(u'主引擎创建成功')

        self.registerEvent()

        le.info(u'注册日志事件监听')


        cfgs = self.cfgs.get('gateway',{}) # 本地加载
        cfgs = self.convertToVnpyGatewayConfig()
        self.mainEngine.connect( cfgs.get('name'),cfgs)

        le.info(u'连接CTP接口')

    def processLogEvent(self,event):
        pass

    def processErrorEvent(event):
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
            req = VtSubscribeReq()
            req.symbol = symbol
            self.mainEngine.subscribe(req, self.cfgs.get('gateway')) # CTP
            self.symbols.add(symbol)

    def unsubscribe(self,*symbols):
        for s in symbols:
            if s in self.symbols:
                self.symbols.remove(s)

    def getSymbols(self):
        return self.symbols


    def procecssTickEvent(self, event):
        """处理行情事件"""
        tick = event.dict_['data']

        # 生成datetime对象
        if not tick.datetime:
            tick.datetime = datetime.strptime(' '.join([tick.date, tick.time]), '%Y%m%d %H:%M:%S.%f')
        self.queue.put(tick)


    def registerEvent(self):
        """注册事件监听"""
        self.ee.register(EVENT_TICK, self.procecssTickEvent)
        self.ee.register(EVENT_LOG, self.processLogEvent)
        self.ee.register(EVENT_ERROR, self.processErrorEvent)

    def _run(self):
        """运行插入线程"""
        while self.active:
            try:
                print 'current tick queue size:', self.queue.qsize()
                # dbName, collectionName, d = self.queue.get(block=True, timeout=1)
                tick  = self.queue.get(block=True, timeout=1)
                chan = instance.messageBrokerManager.get('redis').get('ctp_contract_tick_queue')
                chan.produce( tick.__dict__ )

                symbol = tick.vtSymbol
                name = self.cfgs.get('ctp_contract_tick_pubsub_prefix','')+symbol
                chan = instance.messageBrokerManager.get('redis').create_channel_pubsub(name)
                chan.publish(tick.__dict__)

            except Exception as e:
                pass
