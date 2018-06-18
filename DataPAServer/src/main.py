# coding:utf-8

from gevent.queue import Queue
import json
from threading import Thread
from datetime import datetime, time


from vnpy.trader.vtObject import VtSubscribeReq, VtLogData, VtBarData, VtTickData
from mantis.fundamental.application.app import instance
from mantis.trade.types import ServiceType
from mantis.fundamental.service import ServiceBase
from mantis.trade.service import TradeService
from symbolbar import SymbolBarManager

class PAService(TradeService):
    def __init__(self,name):
        super(TradeService, self).__init__(name)

        self.active = False  # 工作状态
        self.queue = Queue()  # 队列
        self.thread = Thread(target=self._run)  # 线程
        self.logger = instance.getLogger()
        self.symbols = set() # 已经订阅的合约

    def init(self, cfgs):
        self.service_id = cfgs.get('id')
        self.service_type = ServiceType.DataPAServer
        super(PAService,self).init(cfgs)
        SymbolBarManager().init(cfgs.get('generate_bars'))

    def syncDownServiceConfig(self):
        TradeService.syncDownServiceConfig(self)

    def setupFanoutAndLogHandler(self):
        from mantis.trade.log import TradeServiceLogHandler
        self.initFanoutSwitchers(self.cfgs.get('fanout'))
        handler = TradeServiceLogHandler(self)
        self.logger.addHandler(handler)

    def start(self,block=False):
        self.setupFanoutAndLogHandler()
        # 创建日志引擎
        super(PAService,self).start()
        self.active = True
        self.thread.start()


    def stop(self):
        super(PAService,self).stop()
        if self.active:
            self.active = False
            # self.thread.join()

    def join(self):
        self.thread.join()


    def onXminBar(self,scale,bar):
        """
        :param scale:
        :param bar: (VtBarData)
        :return:
        """
        symbol = bar.vtSymbol
        hashobj = bar.__dict__
        hashobj['datetime'] = ''
        hashobj['scale'] = scale
        jsondata = json.dumps(hashobj)
        self.dataFanout('switch0', jsondata, symbol=symbol,scale=scale)


    def onTick(self,symbol,tick):
        """

        :param symbol:
        :param tick: (VtTickData)
        :return:
        """
        SymbolBarManager().ontick(symbol,tick)