# coding:utf-8



import multiprocessing
# from queue import Queue
from gevent.queue import Queue
from threading import Thread
from datetime import datetime, time

# from gevent import queue

from vnpy.event import EventEngine2
from vnpy.trader.vtEvent import EVENT_LOG, EVENT_ERROR,EVENT_TICK
from vnpy.trader.vtEngine import MainEngine, LogEngine
from vnpy.trader.gateway import ctpGateway
from vnpy.trader.vtObject import VtSubscribeReq, VtLogData, VtBarData, VtTickData
from vnpy.trader.vtGateway import *
# from vnpy.trader.app import dataRecorder
# from vnpy.zebra.trade import app
# from vnpy.zebra.contract import update_contract
# from vnpy.zebra.tick import load_cta_tick_subscribe_settings
from mantis.fundamental.application.app import instance

from mantis.fundamental.service import ServiceBase


class MarketService(ServiceBase):
    def __init__(self,name):
        super(ServiceBase, self).__init__(name)

        self.active = False  # 工作状态
        self.queue = Queue()  # 队列
        self.thread = Thread(target=self._run)  # 线程
        self.ee = None
        self.mainEngine = None
        self.logger = instance.getLogger()

    def init(self, cfgs):
        self.cfgs = cfgs


    def start(self,block):
        # 创建日志引擎

        self.active = True
        self.thread.start()

        self.registerEvent()

        le = self.logger
        # le = LogEngine()
        # le.setLogLevel(le.LEVEL_INFO)
        # le.addConsoleHandler()
        le.info(u'启动行情记录运行子进程')

        self.ee = EventEngine2()
        le.info(u'事件引擎创建成功')

        # app().setProp('setting.DataEngine.event.enable', False)
        # app().registerAction('contract_subscribe', load_cta_tick_subscribe_settings)

        me = MainEngine( self.ee,self)
        me.addGateway(ctpGateway)

        le.info(u'主引擎创建成功')

        self.ee.register(EVENT_LOG, self.processLogEvent)
        self.ee.register(EVENT_ERROR, self.processErrorEvent)
        le.info(u'注册日志事件监听')

        cfgs = self.cfgs.get('gateway',{})
        me.connect( cfgs.get('name'),cfgs)

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
        pass

    def join(self):
        self.mainEngine.exit()
        self.thread.join()


    def subscribeTick(self,*symbols):
        for symbol in symbols:
            req = VtSubscribeReq()
            req.symbol = symbol
            self.mainEngine.subscribe(req, self.cfgs.get('gateway')) # CTP


    def procecssTickEvent(self, event):
        """处理行情事件"""
        tick = event.dict_['data']
        vtSymbol = tick.vtSymbol

        # 生成datetime对象
        if not tick.datetime:
            tick.datetime = datetime.strptime(' '.join([tick.date, tick.time]), '%Y%m%d %H:%M:%S.%f')

        # self.onTick(tick)
        self.queue.put(tick)

        # bm = self.bgDict.get(vtSymbol, None)
        # if bm:
        #     bm.updateTick(tick)

    # def insertData(self, dbName, collectionName, data):
    #     """插入数据到数据库（这里的data可以是VtTickData或者VtBarData）"""
    #     self.queue.put((dbName, collectionName, data.__dict__))
    #
    # def onTick(self, tick):
    #     """Tick更新
    #         将Tick发送到redis的持久队列等待被写入mongodb （queue)
    #         将Tick发送到以 合约编号命名的订阅队列 ( pubsub)
    #     """
    #
    #     vtSymbol = tick.vtSymbol


        # if vtSymbol in self.tickSymbolSet:
        #     self.insertData(TICK_DB_NAME, vtSymbol, tick)
        #
        #     # if vtSymbol in self.activeSymbolDict:
        #     #     activeSymbol = self.activeSymbolDict[vtSymbol]
        #     #     self.insertData(TICK_DB_NAME, activeSymbol, tick)
        #     #
        #
        #     self.writeDrLog(text.TICK_LOGGING_MESSAGE.format(symbol=tick.vtSymbol,
        #                                                      time=tick.time,
        #                                                      last=tick.lastPrice,
        #                                                      bid=tick.bidPrice1,
        #                                                      ask=tick.askPrice1))

    def registerEvent(self):
        """注册事件监听"""
        self.ee.register(EVENT_TICK, self.procecssTickEvent)

    def _run(self):
        """运行插入线程"""
        while self.active:
            try:
                print 'current tick queue size:', self.queue.qsize()
                # dbName, collectionName, d = self.queue.get(block=True, timeout=1)
                tick  = self.queue.get(block=True, timeout=1)

                # 这里采用MongoDB的update模式更新数据，在记录tick数据时会由于查询
                # 过于频繁，导致CPU占用和硬盘读写过高后系统卡死，因此不建议使用
                # flt = {'datetime': d['datetime']}
                # self.mainEngine.dbUpdate(dbName, collectionName, d, flt, True)
                # 使用insert模式更新数据，可能存在时间戳重复的情况，需要用户自行清洗
                # try:
                    # self.mainEngine.dbInsert(dbName, collectionName, d)
                # except Exception as e:
                    # self.writeDrLog(u'键值重复插入失败，报错信息：' % traceback.format_exc())
            except Exception as e:
                pass
