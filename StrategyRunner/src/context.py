#coding:utf-8


from mantis.trade.strategy import StrategyTask
from mantis.trade.bar import ArrayManager

class Context(object):
    def __init__(self):
        self.controller = None
        self.props ={}
        self.task = StrategyTask()
        self.toolset = ToolSet

class ToolSet(object):
    ArrayManager = ArrayManager

