#coding:utf-8

"""
St_AJ_MarketRecorder.py
本策略实现行情数据的抓取并存储

"""
import os,sys
from mantis.fundamental.utils.timeutils import current_date_string
from mantis.sg.fisher import stbase
from mantis.sg.fisher import strecoder

from mantis.sg.fisher.tdx.tdx import TDX_StockMarket

class StrategyMarketRecorder(stbase.Strategy):
    """行情记录类策略"""
    def __init__(self,name,product):
        stbase.Strategy.__init__(self,name,product)

    def init(self,*args,**kwargs):
        stbase.Strategy.init(self,*args,**kwargs)

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


    def onBar(self,bar):
        """
        :param bar: stbase.BarData
        :return:
        bar.cycle : ['1m','5m','15m','30m','60m','d','w','m','q','y']
        bar.code :
        bar.trade_object :
        .open .close .high .low .vol .amount .time
        """
        pass
        # if bar.cycle == '5m':
        #     self.sma.execute(bar.code,bar.cycle)


    def start(self):
        # self.set_params(run=self.Runnable.STOP,start='false')  # 停止
        stbase.Strategy.start(self)
        stbase.println("Strategy : Market Recorder Started..")




strategy_id  ='AJ_MarketRecorder'
mongodb_host = '192.168.1.252'

def onInit():
    pid_file = strategy_id +'.pid'
    if sys.argv[-1] == 'stop':
        try:
            pid = int(open(pid_file).read())
            os.kill(pid,9)
        except:
            pass
        sys.exit(0)


    pid = os.getpid()
    open(pid_file,'w').write(str(pid))
    return True


def main():
    onInit()

    from mantis.sg.fisher.stutils import get_trade_database_name
    # 初始化系统参数控制器
    paramctrl = stbase.MongoParamController()
    paramctrl.open(host= mongodb_host , dbname= get_trade_database_name())
    # 策略控制器
    stbase.controller.init('./tdx')
    # 添加运行日志处理
    stbase.controller.getLogger().addAppender(stbase.FileLogAppender('TDX'))
    stbase.controller.setParamController(paramctrl)

    param = paramctrl.get(strategy_id)                  # 读取指定策略id的参数
    conn_url = paramctrl.get_conn_url(param.conn_url)   # 读取策略相关的交易账户信息

    # 初始化行情对象
    market = TDX_StockMarket().init(**conn_url.dict())
    # 添加行情记录器
    market.setupRecorder( strecoder.MarketMongoDBRecorder(db_prefix='TDX_'+current_date_string(), host=mongodb_host))  # 安裝行情記錄器
    # 装备行情对象到股票产品
    stbase.stocks.setupMarket(market)
    # 初始化交易对象
    # trader = TDX_StockTrader().init(**conn_url.dict())
    # stbase.stocks.setupTrader(trader)

    # 初始化策略对象
    strategy = StrategyMarketRecorder(strategy_id,stbase.stocks).init()
    #设置策略日志对象
    # strategy.getLogger().addAppender(strecoder.StragetyLoggerMongoDBAppender(db_prefix='{}_'.format(strategy_id)+current_date_string()+"_",host=mongodb_host))
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