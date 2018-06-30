#coding: utf-8


# context: Context
context = None

def init(ctx):
    #  See : demo/config.yaml
    print ctx.configs


def start(ctx):
    print 'strategy: start()..'
    ctx.controller.setTimer(user='ctp',timeout=2)
    symbols = ctx.configs.get('sub_ticks','').split(',')
    ctx.future.subTicks(symbols[0])
    # ctx.future.subBars(symbols[0],'5m')
    print ctx.future.accounts.keys()    # 配置的期货账户
    print ctx.mongodb
    quota = ctx.future.getAllAccounts()


def stop(ctx):
    print 'strategy: stop()..'


def onTick(tick,ctx):
    """
    tick - mantis.trade.types.TickData
    """
    print 'strategy: onTick()..'
    print 'tick:',tick.symbol
    print 'tick.data', tick.data

def onTrade(trade,ctx):
    """

    :param trade:
    :param ctx:
    :return:
    """
    print 'strategy: onTrade()..'

def onOrder(order,ctx):
    print 'order:',order.product,order.account


def onBar(bar,ctx):
    """
    bar - mantis.trade.types.BarData()
    """
    print 'strategy: onBar()..'
    print 'bar:',bar.symbol,bar.scale
    print 'bar.data:',bar.data

def onTimer(timer,ctx):
    print 'strategy: onTimer()..',timer.timeout,timer.user
    pass

