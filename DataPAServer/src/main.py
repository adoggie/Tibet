# coding:utf-8

import copy
import traceback
from mantis.fundamental.application.use_gevent import USE_GEVENT
if USE_GEVENT:
    from gevent.queue import Queue
    from gevent.lock import RLock
else:
    from Queue import Queue

import json
from threading import Thread
from datetime import datetime as DateTime, time as Time , timedelta as TimeDelta


from vnpy.trader.vtObject import VtSubscribeReq, VtLogData, VtBarData, VtTickData
from mantis.fundamental.application.app import instance
from mantis.trade.types import ServiceType,ProductClass,TimeScale
from mantis.fundamental.service import ServiceBase
from mantis.trade.service import TradeService
from mantis.trade.utils import get_all_contracts,get_symbol_prefix
from symbolbar import SymbolBarManager

from dateutil.parser import parse
from dateutil.rrule import *
import pymongo
import  mantis.trade.kline as kline


class PAService(TradeService):
    def __init__(self,name):
        super(PAService, self).__init__(name)

        self.active = False  # 工作状态
        self.queue = Queue()  # 队列
        self.thread = Thread(target=self._processData)  # 线程
        self.logger = instance.getLogger()
        self.symbols = set() # 已经订阅的合约
        # self.latest_ticks = {}
        self.contracts = {ProductClass.Future:{},ProductClass.Stock:{}}
        self.generate_bars = []
        self.kline_symbols =[]  # 实时计算k线的合约名称
        self.all_calc_mins = {}

    def init(self, cfgs,**kwargs):
        self.service_id = cfgs.get('id')
        self.service_type = ServiceType.DataPAServer
        super(PAService,self).init(cfgs)
        # SymbolBarManager().init(cfgs.get('generate_bars'))
        self.generate_bars = map(str.strip,cfgs.get('generate_bars','').split(','))
        kline.mongodb_conn = instance.datasourceManager.get('mongodb').conn
        self.contracts[ProductClass.Future] = get_all_contracts(type_=ProductClass.Future)

        symbols = self.cfgs.get('kline_symbols','').split(',')
        symbols = map(str.strip,symbols)
        self.kline_symbols = symbols


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
        # self.thread.start()

        self.prepare_kline_calc_minutes()

        self.registerTimedTask(self.make_kline,timeout=1)


    def stop(self):
        super(PAService,self).stop()

        self.active = False


    def join(self):
        # self.thread.join()
        pass


    def onXminBar(self,scale,bar):
        """
        :param scale:
        :param bar: (VtBarData)
        :return:
        """
        symbol = bar.vtSymbol
        self.logger.debug('onXminBar: {} - {}'.format(symbol,scale))

        hashobj = copy.copy(bar.__dict__)

        ## obj.__dict__ 的使用方法，特别注意： 后续修改 hashobj将改变 bar对象的对应的属性值

        hashobj['datetime'] = ''
        hashobj['scale'] = scale
        hashobj.has_key('_id')
        del hashobj['_id']
        jsondata = json.dumps(hashobj)
        self.dataFanout('switch0', jsondata, symbol=symbol,scale=scale)

    def onTick(self,symbol,tick):
        """

        :param symbol:
        :param tick: (VtTickData)
        :return:
        """
        # self.queue.put((symbol,tick))
        # self.latest_ticks[symbol] = tick
        pass

    def _processData(self):
        self.active = True
        while self.active:
            try:
                data = self.queue.get(block=True, timeout=1)
                if not data:
                    continue
                symbol,tick = data
                SymbolBarManager().onTick(symbol, tick)
            except Exception as e:
                # self.logger.error( str(e) )
                # traceback.print_exc()
                pass

    def _make_kline(self,timer):
        """ 定时执行所有合约的k线生成
            生成k线bar发布到redis待写入mongodb
            实时生成指定合约的k线数据，合约定义:  ' kline_symbols'
        """
        # symbols = self.contracts[ProductClass.Future].keys()
        for symbol in self.kline_symbols:

            # prefix = get_symbol_prefix(symbol)
            # 定时生成 合约的1分钟 k线
            bar = kline.make_lastest_min_bar(symbol)
            if bar :
                self.onXminBar('1m',bar)

            for scale in self.generate_bars:
                bar = kline.make_latest_nmin_bar(symbol,scale)
                if bar:
                    self.onXminBar(scale,bar)

        timer.start()

    def prepare_kline_calc_minutes(self):
        """当天载入当日计算时间分钟点和跨日分钟点
            凌晨2：40停止程序运行
        """
        now = DateTime.now()
        if now.time() < Time(3,0):  # 如果在凌晨启动的话，去前一天的计算分钟点
            now = now - TimeDelta(days=1)

        for symbol in self.kline_symbols:
            self.all_calc_mins[symbol] ={}
            for k in (1,5,15,30,60):
                mins = kline.get_day_trade_calc_minutes_new(symbol,k,now)
                self.all_calc_mins[symbol][k] = mins


    def make_kline(self,timer):
        """ 定时执行所有合约的k线生成
            生成k线bar发布到redis待写入mongodb
            实时生成指定合约的k线数据，合约定义:  ' kline_symbols'
        """
        # symbols = self.contracts[ProductClass.Future].keys()
        for symbol in self.kline_symbols:

            # for scale in self.generate_bars:
            for k in (1,5,15,30,60):
                scale = '{}m'.format(k)
                calc_mins = self.all_calc_mins.get(symbol).get(k)

                # 定时生成 合约的1分钟 k线
                bar = kline.make_lastest_min_bar(symbol, scale,calc_mins)
                if bar:
                    self.onXminBar(scale, bar)  # 通知接收用户

        timer.start()
