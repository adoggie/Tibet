#coding:utf-8

from mantis.trade.bar import ArrayManager
from mantis.trade.types import TradeAccountQuota

class Context(object):
    def __init__(self):
        self.controller = None  # controller.StrategyHandler
        self.props ={}
        self.tools = ToolSet
        self.logger = None
        self.future = None  #期货处理对象 handler.futureHandler
        self.stock  = None  #股票处理对象 handler.stockHandler

        self.user = ''      # 交易用户
        self.configs = {}   # 策略运行配置参数 src/strategies/demo/config.yaml
        self.mongodb = None #   mongodb 数据库连接对象



class ToolSet(object):
    ArrayManager = ArrayManager

