#coding:utf-8


"""
pip install tushare==1.2.10 simplejson
"""
import datetime
import json
import numpy as np
import pandas as pa
import talib as ta

import ts_get

from utils.useful import hash_object
from utils.useful import singleton
# /opt/kungfu/master/lib/python2.7/site-packages/kungfu/wingchun
from kungfu.wingchun.constants import *


# STOCK_LIST = ['000001']

bar_log_file ='bar.log'
tick_log_file ='tick.log'

def print_line(text,fp=None):
    text = str(text)
    if fp:
        fp.write(text+'\n')
        fp.flush()
    print text


class StockPosDetail(object):
    def __init__(self):
        self.code = ''  # 股票代码
        self.net_total = 0  # 总持仓
        self.net_yd = 0     # 昨持仓  (可卖数量)

    def __str__(self):
        return 'pos detail({}): {} | {}'.format(self.code,self.net_total,self.net_yd)

class StockTrader(object):
    def __init__(self,code):
        self.code = code
        self.pos = StockPosDetail()  # 持仓信息
        self.pos.code = code

        self.high_price = 0
        self.low_price = 0
        self.last_price = 0
        self.md = None
        self.yd_close_price = 0

    @property
    def yesterday_close_price(self):
        """获取上一个交易日的收盘价"""
        if not self.yd_close_price:
            start = datetime.datetime.now() - datetime.timedelta(days=20)
            start = start.strftime('%Y%m%d')
            end = datetime.datetime.now()
            end = end.strftime('%Y%m%d')
            self.yd_close_price= ts_get.daily(ts_code=self.code,start_date=start,end_date=end).iloc[0]['close']
        return self.yd_close_price

    def __str__(self):
        return 'stock detail: {} ,pos:{},high:{},low:{},last:{}'.format(self.code,str(self.pos),self.high_price,
                                                                        self.low_price,self.last_price)

class KungfuProxy(object):
    def __init__(self,owner):
        self.manager = owner
        self.ctx = None

    def on_init(self,ctx):
        self.ctx = ctx
        # self.manager.init(ctx)
        ctx.add_md(source=SOURCE.XTP)
        ctx.add_td(source=SOURCE.XTP)

        codes = map(lambda s:s.code, self.manager.getStocks())

        ctx.subscribe(tickers=codes, source=SOURCE.XTP)
        ctx.register_bar(source=SOURCE.XTP, min_interval=1, start_time='09:30:00', end_time='15:00:00')
        ctx.register_bar(source=SOURCE.XTP, min_interval=5, start_time='09:30:00', end_time='15:00:00')
        ctx.register_bar(source=SOURCE.XTP, min_interval=15, start_time='09:30:00', end_time='15:00:00')
        ctx.register_bar(source=SOURCE.XTP, min_interval=30, start_time='09:30:00', end_time='15:00:00')
        ctx.register_bar(source=SOURCE.XTP, min_interval=60, start_time='09:30:00', end_time='15:00:00')

        self.ctx.insert_func_after(1, self.on_timer)

    def on_tick(self, md, source, rcv_time):
        code = md.InstrumentID
        stock = TradeManager().getStock(code)
        if stock:
            stock.last_price = md.LastPrice
            stock.high_price = md.HighestPrice
            stock.low_price = md.LowestPrice
            stock.md = md
            # print stock

    def on_bar(self):
        pass

    def on_timer(self):
        # print ">> on_timer"
        self.ctx.req_pos(SOURCE.XTP)
        self.ctx.insert_func_after(1, self.on_timer)

    def on_pos(self, pos_handler, request_id, source, rcv_time):
        # print TradeManager().getStocks()
        for code in  pos_handler.get_tickers():
            stock = TradeManager().getStock(code)
            if stock:
                stock.pos.net_total =  pos_handler.get_net_tot(code)
                stock.pos.net_yd =  pos_handler.get_net_yd(code)
                # print str(stock)
            # print 'code:',code,pos_handler.get_net_tot(code),pos_handler.get_net_yd(code)

    def on_rtn_order(self):
        pass

    def on_rtn_trade(self):
        pass

    def on_error(self):
        pass

    def buy(self,code,num):
        pass

    def sell(self,code,num):
        pass

    def get_ammount(self):
        return 0

class AnyData(object):
    pass

@singleton
class TradeManager(object):
    def __init__(self):
        self.stocks = {}
        self.kf_proxy = KungfuProxy(self)
        self.any = AnyData()

    def init(self):
        return self

    def onTimer(self,ctx):
        pass

    def addStock(self,codes):
        for code in  codes:
            stock = StockTrader(code)
            self.stocks[code] = stock

    def getStock(self,code):
        return self.stocks.get(code)

    def getStocks(self):
        return self.stocks.values()


