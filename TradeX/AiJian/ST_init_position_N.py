#coding:utf-8


"""
ST_init_position_N.py
初始化持仓 为 N 股


"""
import json
import numpy as np
import talib as ta

import os,os.path
from mantis.sg.fisher import stbase
import time
import datetime
from mantis.sg.fisher.utils.timeutils import current_datetime_string

import time,datetime
from collections import OrderedDict
from functools import partial

from mantis.sg.fisher.utils.importutils import import_module
from mantis.sg.fisher.utils.useful import singleton
from mantis.fundamental.utils.timeutils import current_date_string

from mantis.sg.fisher import stbase
from mantis.sg.fisher import ams
from mantis.sg.fisher import strecoder
from mantis.sg.fisher import stsim
from mantis.sg.fisher import stgenerator

# from mantis.sg.fisher.strepo.simple_ma import SimpleMA
# from mantis.sg.fisher.strepo.simple_macd import SimpleMACD
# from mantis.sg.fisher.strepo.simple_bband import SimpleBBand
# from mantis.sg.fisher.strepo.zf_inday import ZFInDay

from  mantis.sg.fisher.strepo import ZFInDay
from mantis.sg.fisher.model import model
from mantis.sg.fisher.tdx.tdx import TDX_StockMarket,TDX_StockTrader



class MyStrategy(stbase.Strategy):
    def __init__(self,name,product):
        stbase.Strategy.__init__(self,name,product)

        # self.sma = SimpleMA(self)
        # self.macd = SimpleMACD(self)
        # self.bband = SimpleBBand(self)
        # self.zf = ZFInDay(self)
        self.open_prices ={
            -0.04: { 'num':100 , 'times':1},
            -0.02: {'num':100, 'times':1}
        }
        self.cover_prices = {
            0.02: {'num':100, 'times':1},
            0.04: {'num':100, 'times':1},
        }
        self.open_allow = True
        self.cover_allow = True



    def init(self,*args,**kwargs):
        stbase.Strategy.init(self,*args,**kwargs)

        return self

    def getSubTickCodes(self):
        return stbase.Strategy.getSubTickCodes(self)

    def getSubBarCodes(self):
        return stbase.Strategy.getSubBarCodes(self)

    def prepared(self):
        delta = datetime.datetime.now() - self.start_time
        return delta.total_seconds() > 5




    def onTick(self,tick):
        """
        :param tick:  stbase.TickData
        :return:
        """
        if self.prepared():
            return

        stbase.println(tick.code, tick.price.last, tick.price.buy_1, tick.price.sell_1)
        cs = self.get_code_params(tick.code)
        print cs.name, cs.strategy_id, cs.enable, cs.value

        print '-'*40
        print ''



        # print tick.dict()
        # print tick.json()
        # print tick.trade_object.limit_price,tick.trade_object.last_price
        # print tick.trade_object.code

        base_price = 0
        # self.strategy_inday(tick.trade_object.code, 100, 0.001)
        # to = stbase.stocks.getTradeObject(tick.trade_object.code)
        # print to.code, to.limit_price,to.last_price

        # self.strategy_inday(tick.trade_object.code, 100, 0.001)
        pass

    def onBar(self,bar):
        """
        :param bar: stbase.BarData
        :return:
        bar.cycle : ['1m','5m','15m','30m','60m','d','w','m','q','y']
        bar.code :
        bar.trade_object :
        .open .close .high .low .vol .amount .time
        """
        # stbase.println(bar.code,bar.cycle,bar.close,bar.vol)
        # print bar.json()
        pass
        # if bar.cycle == '5m':
        #     self.sma.execute(bar.code,bar.cycle)

    def onTimer(self,timer):
        print 'ontimer..'
        N = 100
        codes = self.get_codes()
        for c in codes:
            pos = self.getPosition(c.code)
            if pos.qty_current == 0:
                obj = stbase.stocks.getTradeObject(c.code)
                price = obj.price.sell_1

                print 'Code:',c.code , 'Price:',price
                if price:
                    self.buy(obj.code, price, N )




    def start(self):
        stbase.Strategy.start(self)
        stbase.println("Strategy : Sample Started..")
        self.startTimer(timeout=10)




strategy_id  ='ST_INIT_POS'
mongodb_host = '192.168.1.252'
data_path = './init_pos'

def main():
    from mantis.sg.fisher.stutils import get_trade_database_name
    # 初始化系统参数控制器
    paramctrl = stbase.MongoParamController()
    paramctrl.open(host= mongodb_host,dbname=get_trade_database_name())
    # 策略控制器
    stbase.controller.init(data_path)
    # 添加运行日志处理
    stbase.controller.getLogger().addAppender(stbase.FileLogAppender('TDX'))
    stbase.controller.setParamController(paramctrl)

    param = paramctrl.get(strategy_id)                  # 读取指定策略id的参数
    conn_url = paramctrl.get_conn_url(param.conn_url)   # 读取策略相关的交易账户信息

    # 初始化行情对象
    market = TDX_StockMarket().init(**conn_url.dict())
    # 添加行情记录器
    # market.setupRecorder( strecoder.MarketMongoDBRecorder(db_prefix='TDX_'+current_date_string(), host='192.168.1.252'))  # 安裝行情記錄器
    # 装备行情对象到股票产品
    stbase.stocks.setupMarket(market)
    # 初始化交易对象
    trader = TDX_StockTrader().init(**conn_url.dict())
    stbase.stocks.setupTrader(trader)

    # 初始化策略对象
    strategy = MyStrategy(strategy_id,stbase.stocks).init()
    #设置策略日志对象
    # strategy.getLogger().addAppender(strecoder.StragetyLoggerMongoDBAppender(db_prefix='StrategyLogs_{}_{}'.format(strategy_id,current_date_string() ),host=mongodb_host))
    strategy.getLogger().addAppender(strecoder.StragetyLoggerMongoDBAppender(db_prefix= get_trade_database_name(),host=mongodb_host))
    # 添加策略到 控制器
    stbase.controller.addStrategy(strategy)
    # 控制器运行
    stbase.controller.run()

if __name__ == '__main__':
    main()

"""
mnogodb query statements
----------------------
db.getCollection('AJ_Test1_20190426').find({event:{$in:['order','order_cancel']}},{order_id:1,direction:1,code:1,price:1,oc:1,time:1,quantity:1,_id:0,event:1}).sort({time:-1})

"""