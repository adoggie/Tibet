#coding:utf-8


"""
ST_zf_Inday.py
单日股票振幅买卖策略

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
from mantis.sg.fisher.ctp import CtpMarket, CtpTrader
from mantis.sg.fisher import stutils



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


    def do_zf(self, tick):
        """日内涨跌幅策略
        """

        if not self.prepared():
            print 'System Preparing , Please Wait a while..'
            return

        if not stutils.Stocks.in_trading_time():
            print 'Current is not in Trading Time!'
            return

        # if tick.code != '002517':
        #     return

        code = tick.code
        stock = stbase.stocks.getTradeObject(code)

        # zf = stock.last_price / stock.yd_close - 1
        zf = stock.price.diff_rate

        # strategy_name = 'strategy_inday'
        # st_price = stock.yd_close * (1 + limit)
        # st_price = round(st_price, 2)

        cs = self.get_code_params(tick.code)

        if cs.oc_last != 'open':
            for limit,pp in self.open_prices.items():
                if zf <= limit  :
                    num = pp['num']
                    if stock.price.last < 8 :
                        num = 200

                    pos = self.getPosition(cs.code)
                    if pos.qty_td + num > cs.limit_buy_qty:
                        print code,' open num reached max-limitation!'
                        break

                    st_price = stock.price.sell_1
                    self.logger.takeSignal(stbase.StrategySignal(code, text='strategy_zf_inday, (zf <= limit), '
                                                                            'zf:%s last_price:%s  yd_close_price:%s' %
                                                                            (zf, stock.last_price, stock.yd_close)
                                                                 )
                                           )

                    cs.oc_last = 'open'
                    cs.save()
                    order_req = self.buy(code, st_price, num)
                    break

        if cs.oc_last !='cover':
            for limit,pp in self.cover_prices.items():
                if zf >= limit:
                    num = pp['num']
                    if stock.price.last < 8 :
                        num = 200
                    pos = self.getPosition(cs.code)
                    if pos.qty_yd < num:
                        print code, ' cover num  too less !'
                        break
                    st_price = stock.price.buy_1
                    self.logger.takeSignal(stbase.StrategySignal(code,
                                                                 text='strategy_inday, (zf >= limit), zf:%s last_price:%s  yd_close_price:%s' %
                                                                      (zf, stock.last_price, stock.yd_close)
                                                                 )
                                           )
                    cs.oc_last = 'cover'
                    cs.save()
                    order_req = self.sell(code, st_price, num)
                    break


    def onTick(self,tick):
        """
        :param tick:  stbase.TickData
        :return:
        """
        stock = stbase.futures.getTradeObject(tick.code)

        # 写入交易股票的当前价格
        cp = model.CodePrice.get(code=tick.code)
        if not cp :
            cp = model.CodePrice()
            cp.code = tick.code
            cs = self.get_code_params(tick.code)
            cp.name = cs.name
        cp.assign(tick.price.dict())
        cp.assign(dict(yd_close=stock.yd_close))
        cp.save()

        # 记录当前股票持仓信息
        model.CodePosition.collection().remove({'InstrumentID':tick.code})
        # cp = model.CodePosition.get(code=tick.code,strategy_id=self.id)
        # if not cp:
        #     cp = model.CodePosition()
        for pos in self.getPosition(tick.code): # []
            print pos
        # cp.assign(pos.dict())
        # cp.code = tick.code
        # cs = self.get_code_params(tick.code)
        # cp.name = cs.name
        # cp.strategy_id = self.id
        # cp.save()


        stbase.println(tick.code, tick.price.last, tick.price.buy_1, tick.price.sell_1)
        cs = self.get_code_params(tick.code)
        print cs.name, cs.strategy_id, cs.enable, cs.value
        # self.do_zf(tick)
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
        # timer.start()
        codes = self.get_codes()
        obj = stbase.stocks.getTradeObject( codes[0].code )

        # print obj.last_price,obj.yd_close,obj.limit_price
        # timer.start()
        print self.product.trader.getAmountUsable(),self.product.trader.getAmountUsable()

        # pos = self.getPosition()  # []

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
        codes =  self.get_codes()
        for code in codes:
            self.setCodeParams(code.code,open_allow=True,cover_allow=True)
            print code.code
        self.startTimer()

        stbase.Strategy.start(self)
        stbase.println("Strategy : Sample Started..")

    def onPositionChanged(self):
        """持仓或资金变动事件"""
        print 'Postion Changed..'

    def onRtsChanged(self, rts_list):
        print 'RtsChanged ..'

strategy_id  ='CTP_TRADE1'
mongodb_host = '192.168.1.252'
data_path = './ctp_trade1'
dbname = 'TradeFisherCtp'

def main():
    # from mantis.sg.fisher.stutils import get_trade_database_name
    # 初始化系统参数控制器
    paramctrl = stbase.MongoParamController()
    paramctrl.open(host= mongodb_host,dbname= dbname)
    # 策略控制器
    stbase.controller.init(data_path)
    # 添加运行日志处理
    stbase.controller.getLogger().addAppender(stbase.FileLogAppender('CTP'))
    stbase.controller.setParamController(paramctrl)

    param = paramctrl.get(strategy_id)                  # 读取指定策略id的参数
    conn_url = paramctrl.get_conn_url(param.conn_url)   # 读取策略相关的交易账户信息

    # 初始化行情对象
    market = CtpMarket().init(**conn_url.dict())
    # 装备行情对象到股票产品
    stbase.futures.setupMarket(market)
    # 初始化交易对象
    trader = CtpTrader().init(**conn_url.dict())
    stbase.futures.setupTrader(trader)

    # 初始化策略对象
    strategy = MyStrategy(strategy_id,stbase.futures).init()
    #设置策略日志对象
    strategy.getLogger().addAppender(strecoder.StragetyLoggerMongoDBAppender(db_prefix= dbname,host=mongodb_host))
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