#coding:utf-8


"""
pip install tushare==1.2.10 simplejson
"""
import datetime
import json
import os,os.path
import numpy as np
import pandas as pa
import talib as ta
import time
from threading import Thread,Timer
# import ts_get

from utils.useful import hash_object
from utils.useful import singleton
from utils.timeutils import current_datetime_string,timestamp_current
# /opt/kungfu/master/lib/python2.7/site-packages/kungfu/wingchun
# from kungfu.wingchun.constants import *


# STOCK_LIST = ['000001']

bar_log_file ='bar.log'
tick_log_file ='tick.log'

def print_line(text,fp=None):
    text = str(text)
    if fp:
        fp.write(text+'\n')
        fp.flush()
    print text


class TimedTask(object):
    SECOND = 1
    MINUTE = SECOND * 60

    def __init__(self,action,user_data =None,timeout= SECOND):
        self.action = action
        self.timeout = timeout
        self.start_time = 0
        self.user = user_data
        self.times = 0

    def start(self):
        self.start_time = time.time()
        self.timer = Timer(self.timeout, self.action, (self,))
        self.timer.start()

    def stop(self):
        self.start_time = 0

    # def execute(self):
    #     if self.start_time and self.start_time + self.timeout < time.time():
    #         self.start_time = time.time()
    #         if self.action:
    #             self.action(self)
    #             self.times+=1


class StockPosDetail(object):
    def __init__(self,stock=None):
        # self.stock = stock
        self.code = ''  # 股票代码
        # self.net_total = 0  # 总持仓
        # self.net_yd = 0     # 昨持仓  (可卖数量)
        self.detail = None

    def __str__(self):
        return 'pos detail({}): net_total:{} net_yd:{} net_td:{},' \
               'frozen_yd:{},frozen_td:{},margin_amount:{},' \
               'open_avg_price:{},post_cost_amount:{}'.format(self.code,self.net_total,
                                                                       self.net_yd,
                                                                       self.net_td,
                                                              self.frozen_yd,self.frozen_td,
                                                              self.margin_amount,self.open_avg_price,
                                                              self.post_cost_amount

        )

    @property
    def net_total(self):
        """总持仓"""
        if self.detail:
            return self.detail.PositionQty
        else:
            return 0

    @property
    def net_yd(self):
        """昨持仓"""
        if self.detail:
            return self.detail.YdQty
        else:
            return 0

    @property
    def net_td(self):
        """今持仓"""

        if self.detail:
            return self.detail.TdQty
        else:
            return 0


    @property
    def frozen_yd(self):
        """昨冻结仓"""
        if self.detail:
            return self.detail.TdClosingqty
        else:
            return 0

    @property
    def frozen_td(self):
        """今冻结仓"""
        if self.detail:
            return self.detail.YdClosingqty
        else:
            return 0

    @property
    def margin_amount(self):
        """保证金"""
        if self.detail:
            return self.detail.MarginUsedAmt
        else:
            return 0

    @property
    def open_avg_price(self):
        """开仓均价"""
        if self.detail:
            return self.detail.OpenAvgPrice
        else:
            return 0

    @property
    def post_cost_amount(self):
        """成本金额"""
        if self.detail:
            return self.detail.PostCostAmt
        else:
            return 0

class StockTrader(object):
    def __init__(self,code,ctx=None):
        self.ctx = ctx
        self.code = code
        self.pos = StockPosDetail()  # 持仓信息
        self.pos.code = code

        self.high_price = 0
        self.low_price = 0
        self.last_price = 0
        self.md = None
        self.yd_close_price = 0

        self.stk = None
        self.bar_nums={}  # k线数据最新的bar num编号,用于调取历史k线
        self.bars ={}
        self.bar_handlers={}
        self.tick_handlers=[]

        self.rtn_trade_handlers=[] # 成交回调
        self.order_error_handlers=[]

        self.barlog = None
        self.ticklog = None

        self.init()

    def init(self):
        bar_log_file = '{}/{}-bar.log'.format(TradeManager().logpath,self.code)
        tick_log_file = '{}/{}-tick.log'.format(TradeManager().logpath,self.code)
        self.barlog = open(bar_log_file,'a+')
        self.ticklog = open(tick_log_file,'a+')

        pos_list = self.ctx.Strategy.Product.S_Pos
        for pos in pos_list:
            if pos.ServerCode == self.code:
                self.pos.detail = pos
                print 'detail:',pos

        stk = self.ctx.Market.Stk(self.code)
        stk.MinuteData1.OnNewBar += self.on_bar_m1
        stk.MinuteData5.OnNewBar += self.on_bar_m5
        stk.MinuteData15.OnNewBar += self.on_bar_m15
        stk.MinuteData30.OnNewBar += self.on_bar_m30
        stk.MinuteData60.OnNewBar += self.on_bar_m60
        stk.DailyData.OnNewBar += self.on_bar_daily
        stk.WeeklyData.OnNewBar += self.on_bar_week
        stk.MonthlyData.OnNewBar += self.on_bar_daily
        stk.QuarterlyData.OnNewBar += self.on_bar_quarter
        stk.YearlyData.OnNewBar += self.on_bar_year

        self.bars = dict(m1=stk.MinuteData1,m5=stk.MinuteData5,m15=stk.MinuteData15,m30=stk.MinuteData30,
                         daily=stk.DailyData,week=stk.WeeklyData,month=stk.MonthlyData,
                         quarter=stk.QuarterlyData,year=stk.YearlyData)

        self.bar_nums = dict(m1=0, m5=0, m15=0, m30=0,daily=0, week=0, month=0,quarter=0, year=0)
        self.bar_handlers = dict(m1=[], m5=[], m15=[], m30=[], daily=[], week=[], month=[], quarter=[], year=[])
        stk.OnTick += self.on_tick

        self.stk = stk
        self.last_price = stk.KnockPrice

    def get_ktypes(self):
        return self.bars.keys()

    def get_hist_bars(self,ktype='m1',limit=100):
        """剔除最后一根活动k线"""
        # if self.bar_nums.get(ktype,0) == 0:
        #     return ()
        result=[]

        kdata = self.bars.get(ktype)
        max = kdata.Count
        for num in range(max-limit-1,max-1):  # 不包含最后一根
            d = kdata[num]
            result.append(d)
        return result

    def add_bar_handler(self,handler,ktype='m1'):
        if ktype not in self.bars.keys():
            raise Exception(message='ktype invalid.')
        handlers = self.bar_handlers.get(ktype,[])
        handlers.append(handler)
        return self

    def add_trade_handler(self,hanlder):
        self.rtn_trade_handlers.append(hanlder)
        return self

    def add_tick_handler(self,handler):
        self.tick_handlers.append(handler)
        return self

    def on_rtn_trade(self,trade):
        """触发所有用户定义的成交事件"""

        rt = ReturnTrade(trade)
        for handler in self.rtn_trade_handlers:
            handler(self,rt)

    def on_tick(self,stk):
        self.last_price = stk.KnockPrice

        for handler in self.tick_handlers:
            handler(self,stk)
        fmt = '%Y-%m-%d %H:%M:%S'
        data = dict(KnockTime= time.strftime(fmt,stk.KnockTime),
                    OrderPriceUnit = stk.OrderPriceUnit,
                    ClosePrice = stk.ClosePrice,
                    KnockPrice = stk.KnockPrice,
                    KnockQty = stk.KnockQty,
                    KnockAmt = stk.KnockAmt,
                    TotalKnockQty = stk.TotalKnockQty,
                    TotalKnockAmt = stk.TotalKnockAmt,
                    Diff = stk.Diff,
                    DiffRate = stk.DiffRate,
                    BuyPrice1 = stk.BuyPrice1,
                    SellPrice1 = stk.SellPrice1,
                    BuyQty1 = stk.BuyQty1,
                    SellQty1 = stk.SellQty1
                    )


        data = json.dumps(data)
        TradeManager().save_data(data, self.ticklog)

    def save_bar_data(self,ktype, bar,num):
        # 非交易时间段丢弃
        f = open('{}/{}-{}.txt'.format(TradeManager().logpath,self.code, ktype), 'a+')
        # data = hash_object(bar)
        data = dict( Open=bar.Open,
                     High=bar.High,
                     Low = bar.Low,
                     Close = bar.Close,
                     Vol = bar.Vol,
                     Amount = bar.Amount,
                     DateTime = bar.DateTime
                     )
        print data
        data['bar_num'] = num
        # data = json.dumps(data)
        # f.write(data + '\n')
        # f.close()
        data = json.dumps(data)
        # 写入当前系统时间
        TradeManager().save_data('#{}'.format(current_datetime_string()),f)
        TradeManager().save_data(data,f)
        f.close()

    def bar_data(self,bar):
        data = dict(Open=bar.Open,
                    High=bar.High,
                    Low=bar.Low,
                    Close=bar.Close,
                    Vol=bar.Vol,
                    Amount=bar.Amount,
                    DateTime=bar.DateTime
                    )
        return data

    def on_bar_triggered(self,ktype,bars,num):
        for handler in self.bar_handlers.get(ktype,[]):
            handler(self,bars,num)
        self.save_bar_data(ktype,bars[num],num)

    def on_bar_m1(self,bar,num):
        self.on_bar_triggered('m1',bar,num)

    def on_bar_m5(self,bar,num):
        self.on_bar_triggered('m5',bar,num)

    def on_bar_m15(self,bar,num):
        self.on_bar_triggered('m15', bar, num)

    def on_bar_m30(self,bar,num):
        self.on_bar_triggered('m30', bar, num)

    def on_bar_m60(self,bar,num):
        self.on_bar_triggered('m60', bar, num)

    def on_bar_daily(self,bar,num):
        self.on_bar_triggered('daily', bar, num)

    def on_bar_week(self,bar,num):
        self.on_bar_triggered('week', bar, num)

    def on_bar_month(self,bar,num):
        self.on_bar_triggered('month', bar, num)

    def on_bar_quarter(self,bar,num):
        self.on_bar_triggered('quarter', bar, num)

    def on_bar_year(self,bar,num):
        self.on_bar_triggered('year', bar, num)

    @property
    def yesterday_close_price(self):
        """获取上一个交易日的收盘价"""

        if not self.yd_close_price:
            self.yd_close_price = self.get_hist_bars('daily',2)[-1].Close

        return self.yd_close_price

    def __str__(self):
        return 'stock detail: {} ,pos:{},high:{},low:{},last:{}'.format(self.code,str(self.pos),self.high_price,
                                                                        self.low_price,self.last_price)

class ReturnTrade(object):
    def __init__(self,trade):
        self.detail = trade

    def __str__(self):
        return "Code:{} ".format(self.detail.ServerCode) +\
            "Type:{} ".format(self.detail.Type) +\
            "OrigSerialNo:{} ".format(self.detail.OrigSerialNo) +\
            "BSType:{} ".format(self.detail.BSType) +\
            "OrderFlag:{} ".format(self.detail.OrderFlag) +\
            "ErrCode:{} ".format(self.detail.ErrCode)



class XingyeProxy(object):
    def __init__(self,owner):
        self.manager = owner
        self.ctx = None

        self.fund_change_handlers=[]

    def init(self,ctx):
        self.ctx = ctx
        # self.ctx.Strategy.PosChanged+=self.on_pos
        self.ctx.Strategy.RtsChanged+=self.on_rtn_trade
        self.ctx.Strategy.Product.Changed+=self.on_fund_change

    def on_fund_change(self):
        """"资金变动事件"""
        for handler in self.fund_change_handlers:
            handler()

    def on_rtn_order(self):
        pass

    def on_rtn_trade(self,rts_list):
        """下单成交回调"""
        for rt in rts_list:
            stock = TradeManager().getStock(rt.ServerCode)
            if stock:
                stock.on_rtn_trade(rt)

    def on_error(self):
        pass

    def buy(self,code,price,num):
        order = self.ctx.ResTable.OrderItem(code,'B',num,price)
        return self.ctx.Strategy.Order(order)

    def sell(self,code,price,num):
        order = self.ctx.ResTable.OrderItem(code, 'S', num, price)
        return self.ctx.Strategy.Order(order)

    def get_stock_amount_useable(self):
        """现货可用资金"""
        prd = self.ctx.Strategy.Product
        return prd.Stk_UseableAmt

    def get_stock_amount_asset(self):
        """现货总资产"""
        prd = self.ctx.Strategy.Product
        return prd.Stk_CurrentAmt




class AnyData(object):
    pass

@singleton
class TradeManager(object):
    def __init__(self):
        self.stocks = {}
        # self.kf_proxy = KungfuProxy(self)
        self.xy_proxy = XingyeProxy(self)
        self.any = AnyData()
        self.ctx = None
        self.timers={}
        self.timed_taskes = set()
        self.logpath = 'c:/logdata'
        self.logfile=None

    def init(self,ctx,logpath = 'c:/logdata',logfile='trade-log.txt'):
        self.ctx = ctx

        fmt = '%Y-%m-%d'
        date = time.strftime(fmt, time.localtime())

        self.logpath = os.path.join(logpath,date)
        if not os.path.exists(self.logpath):
            os.mkdir(self.logpath)
        self.logfile = open( os.path.join(self.logpath,logfile),'a+')
        self.xy_proxy.init(ctx)
        # self.addTimer(self.onTimer_1s)
        return self

    def getDataPath(self,name=''):
        return os.path.join(self.logpath,name)

    def onTimer_1s(self,timer):
        print 'onTimer.. 1s'
        timer.start()

    def addTimer(self, action, user=None, timeout=TimedTask.SECOND):
        let = TimedTask(action, user, timeout)
        self.timed_taskes.add(let)
        let.start()
        return let

    def removeTimer(self, let):
        let.stop()
        self.timed_taskes.remove(let)  # don't worry about the lock protection


    def addStocks(self,codes):
        result = None

        for code in  codes:
            code = str(code)
            stock = StockTrader(code,self.ctx)
            self.stocks[code] = stock
            result = stock
        return self

    def addStock(self, code):
        code = str(code)
        stock = StockTrader(code, self.ctx)
        self.stocks[code] = stock
        return stock

    def getStock(self,code):
        return self.stocks.get(code)

    def getStocks(self):
        return self.stocks.values()

    def terminate(self):
        self.ctx.Strategy.Exit()

    def print_line(self,text,fp=None,stdout=True):
        text = str(text)
        if not fp:
            fp = self.logfile
        if fp:
            fp.write(current_datetime_string())
            fp.write(' ')
            fp.write(text + '\n')
            fp.flush()
        if stdout:
            print text

    def save_data(self,text,fp=None):
        text = str(text)
        if fp:
            fp.write(text + '\n')
            fp.flush()
        else:
            print text

    def exit(self):
        self.ctx.Strategy.Exit()

print_line = TradeManager().print_line