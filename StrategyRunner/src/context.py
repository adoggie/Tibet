#coding:utf-8

from mantis.trade.bar import ArrayManager
from mantis.trade.types import TradeAccountQuota

class Context(object):
    def __init__(self):
        self.controller = None
        self.props ={}
        self.tools = ToolSet
        self.logger = None
        self.future = None  #期货处理对象
        self.stock  = None  #股票处理对象

        self.user = ''      # 交易用户
        self.configs = {}   # 策略运行配置参数
        self.quotas = TradeAccountQuota.EMPTY_LIST  # 资金配额

        # = 目前尚未清晰了解 =

        self.positions = {} # 持仓情况
        self.funds = {}     # 账户资金表  { 'futue.htqh01: 200000 , .. }


class ToolSet(object):
    ArrayManager = ArrayManager

