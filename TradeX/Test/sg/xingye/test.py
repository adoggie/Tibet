#coding:utf-8
from utils.useful import hash_object
from functools import partial
import stbase
import simple_st



context = None
print_line = stbase.TradeManager().print_line
def init():
    tm = stbase.TradeManager().init(context,logpath='z:/ams/test')

    # stock = tm.addStock('1000001')
    # stock = tm.addStock('0600006')
    stock = tm.addStock('0600000')
    #
    # stock = tm.addStock('1300252')
    #
    stock.add_tick_handler(on_tick)
    # stock.add_bar_handler(on_bar_m1,'m1')
    # stock.add_bar_handler(on_bar_m5,'m5')
    # stock.add_bar_handler(on_bar_m15,'m15')

    # print '='*20

    print_line(hash_object(context.Strategy.Product))
    prd = context.Strategy.Product
    print_line(prd.Name)
    print_line(prd.Stk_UseableAmt)
    print_line(prd.Stk_CurrentAmt)
    print_line(prd.Stk_StkValue)
    pos_list = prd.S_Pos
    print_line('len:{}'.format(len(pos_list)))
    # pos_list=[]
    for pos in pos_list:
        # if not pos.ServerCode == '1000001':
        if not pos.ServerCode == '0600000':
        # if not pos.ServerCode == '1300252':
            continue
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


    # for bar in stock.get_hist_bars(ktype='week',limit=10):
    #     print_line(stock.bar_data(bar))
    #
    # print 'last_price:{} ,yesterday_close_price:{}'.format(stock.last_price , stock.yesterday_close_price)

    # simple_st.strategy_ma(stock.code,5)


    print_line('get_stock_amount_useable:%s'%stbase.TradeManager().xy_proxy.get_stock_amount_useable())
    print_line('get_stock_amount_asset:%s'%stbase.TradeManager().xy_proxy.get_stock_amount_asset())

    print_line('pos detail:%s'% stock.pos)

    # bars = stock.get_hist_bars('m1', limit=30)
    bars = stock.get_hist_bars('m5', limit=30)
    close = map(lambda _: _.Close, bars)

    print_line(close)

    # test - ordering

    stbase.TradeManager().addTimer(on_timer)
    stock.add_trade_handler(on_trade)

    # print 'code:',stock.code
    # print 'net_yd:',stock.pos.net_yd
    # print str(stock)


def on_trade(sotck,trade):
    """成交回调"""
    detail = trade.detail
    print_line("="*20)
    print_line(str(trade))

def on_timer(timer):
    # print 'in timer..'
    timer.start()

def on_tick(stock,stk):
    import simple_st
    # simple_st.strategy_inday(stock.code)

    # stk = stock.stk
    # print_line(stk.ServerCode,stk.KnockPrice,stk.KnockTime,stk.BuyPrice1
    print_line(stock.last_price)
    if not context.data.get('buy',False):
        print 'do buy()..'
        # order_no = stbase.TradeManager().xy_proxy.buy(stock.code,stock.last_price,100)
        order_no = stbase.TradeManager().xy_proxy.sell(stock.code,stock.last_price,100)
        context.data['buy'] = True
        print 'order_no is:'+ str(order_no)


def on_bar_m1(stock,bar,num):
    print_line( '{},{},{}'.format(stock.code,bar[num] ,num),stdout=True)
    # print_line(hash_object(bar[num]))

def on_bar_m5(stock,bar,num):
    print_line('{},{},{}'.format(stock.code, bar[num], num))

def on_bar_m15(stock,bar,num):
    import simple_st
    print_line('{},{},{}'.format(stock.code, bar[num], num))
    simple_st.strategy_ma(stock.code,15)

def on_bar_m30(stock,bar,num):
    print_line('{},{},{}'.format(stock.code, bar[num], num))

print_line('main start..')

'''
（1）交易端首页登录账号/密码：zssp000/xyzq601377；
其现货资金账号/密码：30073627/112233

兴业-云服务器账号
================
账号：XYXY001
密码：XYXY0000

'''