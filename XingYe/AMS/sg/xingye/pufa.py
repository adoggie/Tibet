#coding:utf-8

"""
日内涨跌幅连续买入卖出

"""
from utils.useful import hash_object
from functools import partial
import stbase
import simple_st



context = None
print_line = stbase.TradeManager().print_line
def init():
    tm = stbase.TradeManager().init(context,logpath='z:/ams/pufa',
                                    strategy_name='pufa') # 不保存行情数据

    codes=['1000001','1300252','1300310','1300025','0600000']
    # stock = tm.addStock('0600000')
    # stock = tm.addStock('1300310') #宜通世纪
    stocks = []
    for code in codes:
        stock = tm.addStock(code)
        stocks.append(stock)
        stock.add_tick_handler(on_tick)


def on_tick(stock,stk):
    base_price = 0
    strategy_inday(stock.code,100,0.001,base_price)
    stk = stock.stk
    # print_line(stk.ServerCode,stk.KnockPrice,stk.KnockTime,stk.BuyPrice1
    # simple_st.strategy_ma(stock.code, 1)

def on_bar_m1(stock,bar,num):
    print_line( '{},{},{}'.format(stock.code,bar[num] ,num))
    # print_line(hash_object(bar[num]))
    simple_st.strategy_ma(stock.code, 1)

def on_bar_m5(stock,bar,num):
    print_line('{},{},{}'.format(stock.code, bar[num], num))
    simple_st.strategy_ma(stock.code, 5)

def on_bar_m15(stock,bar,num):
    import simple_st
    print_line('{},{},{}'.format(stock.code, bar[num], num))
    simple_st.strategy_ma(stock.code,15)

def on_bar_m30(stock,bar,num):
    print_line('{},{},{}'.format(stock.code, bar[num], num))

# print_line('main start..')


def strategy_inday(code,num = 100 ,limit=0.02,base_price=0 ):
    """日内涨跌幅策略
    @:param code: 股票代码
    @:param num ：买卖数量
    @:param limit: 价格浮动限
    base_price : 参考基准价格 ， 0 表示采用昨收盘价格

    当日仅仅允许买卖各触发一次

    """

    stock = stbase.TradeManager().getStock(code)

    if base_price == 0:
        zf =  stock.last_price / stock.yesterday_close_price - 1
    else:
        zf = stock.last_price / base_price - 1

    st_price =  stock.yesterday_close_price * (1+limit)
    st_price = round(st_price,2)
    # stbase.println('st_price:%s  '%st_price)
    stbase.println('zf:{} limit:{} diff:{}'.format(zf, limit,zf-limit))

    if zf <= -limit and stock.any.flag_buy:
        stbase.print_line('(strategy_inday) zf:%s last_price:%s  base_price:%s' % (zf, stock.last_price, base_price))

        stbase.record_signal(code,'=={}=='.format(code))
        stbase.record_signal(code,'strategy_inday signal occur. (zf <= -limit)')
        stbase.record_signal(code,'zf:{} limit:{}'.format(zf,limit))
        #跌幅过限
        amount = stbase.TradeManager().xy_proxy.get_stock_amount_useable()
        pos_sum = stock.pos.net_total
        #
        if stock.pos.post_cost_amount <= amount * 0.1  :
            """持仓资金占总资金 <= 10% """
            stbase.record_signal(code,'do buy: {} ,{}, {}'.format(code,st_price, num))
            stbase.TradeManager().xy_proxy.buy(code,st_price,num)
            strategy_inday_buy_count[code]=1
            stock.any.flag_buy = 0
            stock.any.flag_sell = 1


    if zf >= limit and stock.any.flag_sell:
        # print '=*'*20
        stbase.print_line('(strategy_inday) zf:%s last_price:%s  base_price:%s' % (
        zf, stock.last_price, base_price))

        stbase.TM.record_signal(code,'=={}=='.format(code))
        stbase.TM.record_signal(code,'-*' * 20)
        stbase.TM.record_signal(code,'strategy_inday signal occur. (zf >= -limit)')
        stbase.TM.record_signal(code,'zf:{} limit:{}'.format(zf, limit))
        stbase.TM.record_signal(code,'net_total:{} net_yd:{}'.format(stock.pos.net_total,stock.pos.net_yd))
        if stock.pos.net_total >= num :
            stbase.TM.record_signal(code,'do sell: {} ,{}, {}'.format(code, st_price,num))
            stbase.TradeManager().xy_proxy.sell(code,st_price,num)
            strategy_inday_sell_count[code]=1
            stock.any.flag_sell = 0
            stock.any.flag_buy = 1



'''
（1）交易端首页登录账号/密码：zssp000/xyzq601377；
其现货资金账号/密码：30073627/112233

兴业-云服务器账号
================
账号：XYXY001
密码：XYXY0000
'''