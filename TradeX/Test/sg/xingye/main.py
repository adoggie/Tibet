#coding:utf-8
from utils.useful import hash_object
from functools import partial
import stbase
import simple_st



context = None
print_line = stbase.TradeManager().print_line
def init():
    tm = stbase.TradeManager().init(context,logpath='z:/ams/logpath')

    stock = tm.addStock('1000001')

    stock2 = tm.addStock('1300252')
    stock3 = tm.addStock('1300310')
    stock4 = tm.addStock('1300025')

    stock.add_tick_handler(on_tick)
    stock2.add_tick_handler(on_tick)
    stock3.add_tick_handler(on_tick)
    stock4.add_tick_handler(on_tick)


    # stock.add_bar_handler(on_bar_m1,'m1')
    stock.add_bar_handler(on_bar_m5,'m5')
    stock.add_bar_handler(on_bar_m15,'m15')

    stock2.add_bar_handler(on_bar_m5, 'm5')
    stock2.add_bar_handler(on_bar_m15, 'm15')

    stock3.add_bar_handler(on_bar_m5, 'm5')
    stock3.add_bar_handler(on_bar_m15, 'm15')

    stock4.add_bar_handler(on_bar_m5, 'm5')
    stock4.add_bar_handler(on_bar_m15, 'm15')


    print_line(hash_object(context.Strategy.Product))
    prd = context.Strategy.Product
    print_line(prd.Name)
    print_line(prd.Stk_UseableAmt)
    print_line(prd.Stk_CurrentAmt)
    print_line(prd.Stk_StkValue)
    pos_list = prd.S_Pos
    print_line('len:{}'.format(len(pos_list)))
    pos_list=[]
    for pos in pos_list:
        print_line('ServerCode:{}'.format(pos.ServerCode))
        print_line('BsFlag:{}'.format(pos.BsFlag))
        print_line('CurrentQty:{}'.format(pos.CurrentQty))
        print_line('PositionQty:{}'.format(pos.PositionQty))
        print_line('TDTotalQty:{}'.format(pos.TDTotalQty))
        print_line('YdQty:{}'.format(pos.YdQty))
        print_line('TdQty:{}'.format(pos.TdQty))
        print_line('YdClosingqty:{}'.format(pos.YdClosingqty))
        print_line('TdClosingqty:{}'.format(pos.TdClosingqty))
        print_line('MarginUsedAmt:{}'.format(pos.MarginUsedAmt))
        print_line('OpenAvgPrice:{}'.format(pos.OpenAvgPrice))
        print_line('PostCostAmt:{}'.format(pos.PostCostAmt))
        print_line('--'*20)


    for bar in stock.get_hist_bars(ktype='week',limit=10):
        print_line(stock.bar_data(bar))

    print 'last_price:{} ,yesterday_close_price:{}'.format(stock.last_price , stock.yesterday_close_price)

    # simple_st.strategy_ma(stock.code, 15)
    # simple_st.strategy_ma(stock.code, 1)

def on_tick(stock,stk):
    import simple_st
    simple_st.strategy_inday(stock.code)
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

'''
（1）交易端首页登录账号/密码：zssp000/xyzq601377；
其现货资金账号/密码：30073627/112233

兴业-云服务器账号
================
账号：XYXY001
密码：XYXY0000
'''