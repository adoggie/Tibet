#coding: utf-8


# context: Context
context = None

def init(ctx):
    #  See : demo/config.yaml
    print ctx.configs



def test_send_orders(timer):
    # context.future.buy('bu1812',3776,1)
    print context.future.buy('hc1901',3910,1)

def start(ctx):
    print 'strategy: start()..'
    # ctx.controller.setTimer(user='ctp',timeout=2)
    symbols = ctx.configs.get('sub_ticks','').split(',')
    # ctx.future.subTicks(symbols[0])
    ctx.future.subTicks('i1901')

    #测试发单
    ctx.controller.setTimer(test_send_orders,timeout=3)

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
    quota = ctx.future.getAllAccounts()
    print quota
    ctx.props['cc'] = 0

def stop(ctx):
    print 'strategy: stop()..'


def onTick(tick,ctx):
    """
    tick - mantis.trade.types.TickData
    """
    print 'strategy: onTick()..','-- ',tick.symbol,' --'
    # print tick.__dict__
    print tick.lastPrice


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
