# coding:utf-8

# context: Context
context = None

def init(ctx):
    #  See : demo/config.yaml
    print ctx.task.strategy.configs

def start(ctx):
    print 'strategy: start()..'
    ctx.controller.setTimer(user='ctp',timeout=2)
    symbols = ctx.task.strategy.params.get('sub_ticks','').split(',')
    # ctx.controller.subTicks(symbols[0])
    ctx.controller.subBars(symbols[0],'5m')

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
    print 'strategy: onTrade()..'

def onBar(bar,ctx):
    """
    bar - mantis.trade.types.BarData()
    """
    print 'strategy: onBar()..'
    print 'bar:',bar.symbol,bar.scale
    print 'bar.data:',bar.data

def onTimer(timer,ctx):
    # print 'strategy: onTimer()..',timer.timeout,timer.user
    pass

