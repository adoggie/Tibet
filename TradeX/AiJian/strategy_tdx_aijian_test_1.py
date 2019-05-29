#coding:utf-8



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

from mantis.sg.fisher.tdx.tdx import TDX_StockMarket,TDX_StockTrader

class MyStrategy(stbase.Strategy):
    def __init__(self,name,product):
        stbase.Strategy.__init__(self,name,product)

        # self.sma = SimpleMA(self)
        # self.macd = SimpleMACD(self)
        # self.bband = SimpleBBand(self)
        self.zf = ZFInDay(self)

    def init(self,*args,**kwargs):
        stbase.Strategy.init(self,*args,**kwargs)
        self.any = dict( inday_buy_count = {},  # 意图控制买卖下单的次数
                        inday_sell_count = {}
                         )
        return self

    def getSubTickCodes(self):
        return stbase.Strategy.getSubTickCodes(self)

    def getSubBarCodes(self):
        return stbase.Strategy.getSubBarCodes(self)

    def onTick(self,tick):
        """
        :param tick:  stbase.TickData
        :return:
        """
        # self.zf.onTick(tick)
        stbase.println(tick.code,tick.price.last,tick.price.buy_1,tick.price.sell_1)
        cs = self.get_code_params(tick.code)
        print cs.name,cs.strategy_id , cs.enable , cs.value

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
        # timer.start()
        codes = self.get_codes()
        obj = stbase.stocks.getTradeObject( codes[0].code )

        # print obj.last_price,obj.yd_close,obj.limit_price
        timer.start()
        print self.product.trader.getAmountUsable(),self.product.trader.getAmountUsable()


        # print obj.price.dict()
        # print 'on buy() or sell() ..'
        # self.buy('0600000',obj.price.sell_1,100)
        # self.sell('0600000',obj.price.buy_1,100)

        # 以最低价下委托买入
        # for _ in range(1):
        #     stbase.println('try buy({})..'.format(obj.min_price))
        #     self.buy(code,obj.min_price,100)
        #     #
        #     # stbase.println('try sell({})..'.format(30))
        #     # self.sell(code, obj.max_price, 100)
        #     time.sleep(1)

    def cancel_all_orders(self,task):
        for _  in  self.getOrders():
            # print _.dict()
            # print _.code,_.order_id
            print 'cancel order_id:' , _.order_id
            self.cancelOrder(_.order_id)

        # if not self.getOrders():
        self.startTimer(self.make_orders, timeout=5)
        pass

    def make_orders(self,task):
        obj = stbase.stocks.getTradeObject('002517')
        H,L = obj.limit_price
        print 'do  orders ..',H,L
        self.buy(obj.code,L,100)
        self.sell(obj.code,H,100)
        self.startTimer(self.cancel_all_orders,timeout=5)
        # task.start()

    def limit_buy(self,task):
        price = stbase.stocks.getTradeObject('002517').price
        print price.sell_1 , price.sell_qty_1 , price.sell_2 ,price.sell_qty_2

        # for _ in self.getPosition():
        #     print _.dict()
        print self.getPosition('002517').dict()
        task.start()

    def start(self):
        self.set_params(run=self.Runnable.STOP,start='false')  # 停止
        print self.get_codes()

        stbase.Strategy.start(self)
        stbase.println("Strategy : Sample Started..")

        # self.startTimer(self.cancel_all_orders,timeout=5)
        # self.startTimer(self.make_orders,timeout=5)
        # self.startTimer(self.limit_buy,timeout=5)

        # for _ in  stbase.stocks.market.getHistoryBars(self.CODES[0],limit=5):
        #     print _.time
        # code = '0600000'
        # to = stbase.stocks.getTradeObject(code)
        # pos = self.product.getPosition(code)
        # stbase.println(pos.dict())
        # amount = self.product.getAmountUsable()
        # asset = self.product.getAmountAsset()

        # stbase.println('amount:{}'.format(amount) )
        # stbase.println('asset:{}'.format(asset)  )

        # self.startTimer(timeout=1)
        # return

        # 打印持仓信息
        # pos_list = self.getPosition()
        # for pos in pos_list:
        #     stbase.println( 'code:%s , yd_qty:%s'%(pos.code,pos.qty_yd))
        #
        # 打印委托记录（在委托中..)
        # orders = self.getOrders(order_id=111)
        # orders = self.getOrders()
        # for order in orders:
        #     stbase.println( order )
        #     self.cancelOrder(order.order_id)

        # self.cancelOrder(390941)

    def onPositionChanged(self):
        """持仓或资金变动事件"""
        print 'Postion Changed..'

    def onRtsChanged(self, rts_list):
        print 'RtsChanged ..'


def main():
    strategy_id  ='AJ_Test1'
    # 初始化系统参数控制器
    paramctrl = stbase.MongoParamController()
    paramctrl.open(host='192.168.1.252')
    # 策略控制器
    stbase.controller.init('z:/ams/tdx')
    # 添加运行日志处理
    stbase.controller.getLogger().addAppender(stbase.FileLogAppender('TDX'))
    stbase.controller.setParamController(paramctrl)

    param = paramctrl.get(strategy_id)                  # 读取指定策略id的参数
    conn_url = paramctrl.get_conn_url(param.conn_url)   # 读取策略相关的交易账户信息

    # 初始化行情对象
    market = TDX_StockMarket().init(**conn_url.dict())
    # 添加行情记录器
    market.setupRecorder( strecoder.MarketMongoDBRecorder(db_prefix='TDX_'+current_date_string(), host='192.168.1.252'))  # 安裝行情記錄器
    # 装备行情对象到股票产品
    stbase.stocks.setupMarket(market)
    # 初始化交易对象
    trader = TDX_StockTrader().init(**conn_url.dict())
    stbase.stocks.setupTrader(trader)

    # 初始化策略对象
    strategy = MyStrategy(strategy_id,stbase.stocks).init()
    #设置策略日志对象
    strategy.getLogger().addAppender(strecoder.StragetyLoggerMongoDBAppender(db_prefix='{}_'.format(strategy_id)+current_date_string()+"_",host='192.168.1.252'))
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