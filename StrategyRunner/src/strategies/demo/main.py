#coding: utf-8

from vnpy.trader.vtConstant import *
context = None

def init(ctx):
    #  See : demo/config.yaml
    print ctx.configs

def test_send_orders(timer):
    """测试以跌停价下单买开"""
    for x in range(3):
        print 'Send Order..(Buy)','IF1809',2950,1
        print context.future.buy('IF1809',2950,1)
        context.tools.sleep(1)


    context.controller.setTimer(test_orders_query_and_cancel, timeout=5)

def test_orders_query_and_cancel(timer):
    """查询订单并全部撤单"""
    rs = context.future.getAllOrders()
    for order in rs:
        print order.__dict__
        if order.status == STATUS_NOTTRADED:
            print 'Cancel Order..'
            print order.symbol, order.vtOrderID
            context.future.cancelOrder(order.vtOrderID)
            gevent.sleep(1)

    context.controller.setTimer(test_send_orders, timeout=3)
    # timer.start()

def test_order_buy_open(timer):
    """以当前价买开"""
    tick = context.props['tick']
    last_price = tick.askPrice1
    #已最新成交价格买入
    print context.future.buy('IF1809',last_price,1)
    #买入之后进行卖出
    context.controller.setTimer(test_order_sell_close, timeout=5)

def test_order_sell_close(timer):
    """已当前卖价卖平指定合约"""
    tick = context.props['tick']
    last_price = tick.bidPrice1
    print 'sell close , price:',last_price
    print context.future.sell('IF1809',last_price,1)

    context.controller.setTimer(test_order_buy_open, timeout=3)

def start(ctx):
    print 'strategy: start()..'
    # ctx.controller.setTimer(user='ctp',timeout=2)
    symbols = ctx.configs.get('sub_ticks','').split(',')
    # ctx.future.subTicks(symbols[0])
    # ctx.future.subTicks('i1901')
    ctx.future.subTicks('IF1809')

    #测试发单
    # ctx.controller.setTimer(test_send_orders,timeout=3)
    # ctx.controller.setTimer(test_order_buy_open,timeout=3)
    # ctx.controller.setTimer(test_order_sell_close,timeout=3)

    # ctx.controller.setTimer(test_orders_query_and_cancel,timeout=3)

    # ctx.future.subTicks('AP901') # master product in night.
    # ctx.future.subBars('AP901','1m') # master product in night.
    #
    # ticks = ctx.future.loadTicks('AP901', 10)
    # print 'loadTicks:', len(ticks) , ticks[0].__dict__
    #
    # bars = ctx.future.loadBars('AP901','1m',10)
    # print 'loadBars:',len(bars), bars[0].__dict__
    #
    # # ctx.future.subBars(symbols[0],'5m')
    print ctx.future.accounts.keys()    # 配置的期货账户
    print 'MongoDB connection:',ctx.mongodb

    # 获取策略配额账户信息
    quota = ctx.future.getAllAccounts()
    print quota

    # 获取合约信息测试
    data = ctx.future.get_contract_data('IF1809')
    print data.dict()


def stop(ctx):
    print 'strategy: stop()..'


def onTick(tick,ctx):
    """
    tick - mantis.trade.types.TickData
    """
    # print 'strategy: onTick()..','-- ',tick.symbol,' --'
    print tick.__dict__
    # print tick.symbol,tick.lastPrice
    context.props['tick'] = tick
    pass



def onTrade(trade,ctx):
    print 'strategy: onTrade()..'
    print trade.__dict__

def onOrder(order,ctx):
    print 'order:'
    print order.__dict__

def onPosition(position,ctx):
    # print position.__dict__
    pass

def onAccount(account,ctx):
    # print account.__dict__
    pass

def onBar(bar,ctx):
    """
    bar - mantis.trade.types.BarData()
    """
    print 'strategy: onBar()..',bar.symbol

    print bar.__dict__

def onTimer(timer,ctx):
    print 'strategy: onTimer()..',timer.timeout,timer.user
    if ctx.props['cc'] == 0:
        print ctx.future.buy('ag1812',3423,1)
        ctx.props['cc']+=1

    timer.start()
