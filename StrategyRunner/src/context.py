#coding:utf-8

from mantis.trade.bar import ArrayManager
from mantis.trade.types import TradeAccountQuota
from vnpy.trader.vtConstant import *
import  gevent 

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




class CtpConstantsOrderPriceType(object):
    """详细见 ctp_data_type.py , ThostFtdUserApiDataType.h , """
    # 任意价
    AnyPrice = '1'
    # 限价
    LimitPrice = '2'
    # 最优价
    BestPrice = '3'
    # 最新价
    LastPrice = '4'
    # 最新价浮动上浮1个ticks
    LastPricePlusOneTicks = '5'
    # 最新价浮动上浮2个ticks
    LastPricePlusTwoTicks = '6'
    # 最新价浮动上浮3个ticks
    LastPricePlusThreeTicks = '7'
    # 卖一价
    AskPrice1 = '8'
    # 卖一价浮动上浮1个ticks
    AskPrice1PlusOneTicks = '9'
    # 卖一价浮动上浮2个ticks
    AskPrice1PlusTwoTicks = 'A'
    # 卖一价浮动上浮3个ticks
    AskPrice1PlusThreeTicks = 'B'
    # 买一价
    BidPrice1 = 'C'
    # 买一价浮动上浮1个ticks
    BidPrice1PlusOneTicks = 'D'
    # 买一价浮动上浮2个ticks
    BidPrice1PlusTwoTicks = 'E'
    # 买一价浮动上浮3个ticks
    BidPrice1PlusThreeTicks = 'F'
    # 五档价
    FiveLevelPrice = 'G'
    # 本方最优价
    BestPriceThisSide = 'H'

    PRICETYPE_LIMITPRICE = PRICETYPE_LIMITPRICE
    PRICETYPE_MARKETPRICE = PRICETYPE_MARKETPRICE
    PRICETYPE_FAK = PRICETYPE_FAK
    PRICETYPE_FOK = PRICETYPE_FOK


class ToolSet(object):
    ArrayManager = ArrayManager
    CtpConstantsOrderPriceType = CtpConstantsOrderPriceType
    sleep = gevent.sleep

__all__ = (Context,)