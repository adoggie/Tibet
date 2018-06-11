#coding:utf-8

class Context(object):
    def __init__(self):
        self.controller = None
        self.props ={}
        self.event = StrategyEvent()



class StrategyEvent(object):
    def __init__(self,tick=None,order=None,trade=None,bar=None):
        self.onTick = tick
        self.onOrder = order
        self.onTrade = trade
        self.onBar = bar