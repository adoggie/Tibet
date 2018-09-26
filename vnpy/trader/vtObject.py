# encoding: UTF-8

import time
from logging import INFO

from vnpy.trader.vtConstant import (EMPTY_STRING, EMPTY_UNICODE, 
                                    EMPTY_FLOAT, EMPTY_INT)


########################################################################
class VtBaseData(object):
    """回调函数推送数据的基础类，其他数据类继承于此"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.gatewayName = EMPTY_STRING         # Gateway名称        
        self.rawData = None                     # 原始数据

 
########################################################################
class VtTickData(VtBaseData):
    """Tick行情数据类"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        super(VtTickData, self).__init__()
        
        # 代码相关
        self.symbol = EMPTY_STRING              # 合约代码
        self.exchange = EMPTY_STRING            # 交易所代码
        self.vtSymbol = EMPTY_STRING            # 合约在vt系统中的唯一代码，通常是 合约代码.交易所代码
        
        # 成交数据
        self.lastPrice = EMPTY_FLOAT            # 最新成交价
        self.lastVolume = EMPTY_INT             # 最新成交量
        self.volume = EMPTY_INT                 # 今天总成交量
        self.openInterest = EMPTY_INT           # 持仓量
        self.time = EMPTY_STRING                # 时间 11:20:56.5
        self.date = EMPTY_STRING                # 日期 20151009
        self.datetime = None                    # python的datetime时间对象
        
        # 常规行情
        self.openPrice = EMPTY_FLOAT            # 今日开盘价
        self.highPrice = EMPTY_FLOAT            # 今日最高价
        self.lowPrice = EMPTY_FLOAT             # 今日最低价
        self.preClosePrice = EMPTY_FLOAT
        
        self.upperLimit = EMPTY_FLOAT           # 涨停价
        self.lowerLimit = EMPTY_FLOAT           # 跌停价
        
        # 五档行情
        self.bidPrice1 = EMPTY_FLOAT
        self.bidPrice2 = EMPTY_FLOAT
        self.bidPrice3 = EMPTY_FLOAT
        self.bidPrice4 = EMPTY_FLOAT
        self.bidPrice5 = EMPTY_FLOAT
        
        self.askPrice1 = EMPTY_FLOAT
        self.askPrice2 = EMPTY_FLOAT
        self.askPrice3 = EMPTY_FLOAT
        self.askPrice4 = EMPTY_FLOAT
        self.askPrice5 = EMPTY_FLOAT        
        
        self.bidVolume1 = EMPTY_INT
        self.bidVolume2 = EMPTY_INT
        self.bidVolume3 = EMPTY_INT
        self.bidVolume4 = EMPTY_INT
        self.bidVolume5 = EMPTY_INT
        
        self.askVolume1 = EMPTY_INT
        self.askVolume2 = EMPTY_INT
        self.askVolume3 = EMPTY_INT
        self.askVolume4 = EMPTY_INT
        self.askVolume5 = EMPTY_INT

        self.ts  = 0            # 行情时间戳
        self.ts_host = 0        # 主机系统时间戳
        self.source = 'tick'    # tick/pad 行情tick(tick)/还是填充tick(pad)
        self.mp = EMPTY_STRING  # market product  , AU,AG,IF,..

    
########################################################################
class VtBarData(VtBaseData):
    """K线数据"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        super(VtBarData, self).__init__()
        
        self.vtSymbol = EMPTY_STRING        # vt系统代码
        self.symbol = EMPTY_STRING          # 代码
        self.exchange = EMPTY_STRING        # 交易所
    
        self.open = EMPTY_FLOAT             # OHLC
        self.high = EMPTY_FLOAT
        self.low = EMPTY_FLOAT
        self.close = EMPTY_FLOAT
        
        self.date = EMPTY_STRING            # bar开始的时间，日期
        self.time = EMPTY_STRING            # 时间
        self.datetime = None                # python的datetime时间对象
        
        self.volume = EMPTY_INT             # 成交量
        self.openInterest = EMPTY_INT       # 持仓量

        self.scale = ''         # bar 的时间刻度 1m,2m,..
        self.product = ''       # 期货还是股票
    

########################################################################
class VtTradeData(VtBaseData):
    """成交数据类"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        super(VtTradeData, self).__init__()
        
        # 代码编号相关
        self.symbol = EMPTY_STRING              # 合约代码
        self.exchange = EMPTY_STRING            # 交易所代码
        self.vtSymbol = EMPTY_STRING            # 合约在vt系统中的唯一代码，通常是 合约代码.交易所代码
        
        self.tradeID = EMPTY_STRING             # 成交编号
        self.vtTradeID = EMPTY_STRING           # 成交在vt系统中的唯一编号，通常是 Gateway名.成交编号
        
        self.orderID = EMPTY_STRING             # 订单编号
        self.vtOrderID = EMPTY_STRING           # 订单在vt系统中的唯一编号，通常是 Gateway名.订单编号
        
        # 成交相关
        self.direction = EMPTY_UNICODE          # 成交方向
        self.offset = EMPTY_UNICODE             # 成交开平仓
        self.price = EMPTY_FLOAT                # 成交价格
        self.volume = EMPTY_INT                 # 成交数量
        self.tradeTime = EMPTY_STRING           # 成交时间

        #
        self.request_id = EMPTY_INT
        self.strategy_id = EMPTY_STRING  # 关联的策略编号

########################################################################
class VtOrderData(VtBaseData):
    """订单数据类"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        super(VtOrderData, self).__init__()
        
        # 代码编号相关
        self.symbol = EMPTY_STRING              # 合约代码
        self.exchange = EMPTY_STRING            # 交易所代码
        self.vtSymbol = EMPTY_STRING            # 合约在vt系统中的唯一代码，通常是 合约代码.交易所代码
        
        self.orderID = EMPTY_STRING             # 订单编号
        self.vtOrderID = EMPTY_STRING           # 订单在vt系统中的唯一编号，通常是 Gateway名.订单编号
        
        # 报单相关
        self.direction = EMPTY_UNICODE          # 报单方向
        self.offset = EMPTY_UNICODE             # 报单开平仓
        self.price = EMPTY_FLOAT                # 报单价格
        self.totalVolume = EMPTY_INT            # 报单总数量
        self.tradedVolume = EMPTY_INT           # 报单成交数量
        self.status = EMPTY_UNICODE             # 报单状态
        
        self.orderTime = EMPTY_STRING           # 发单时间
        self.cancelTime = EMPTY_STRING          # 撤单时间
        
        # CTP/LTS相关
        self.frontID = EMPTY_INT                # 前置机编号
        self.sessionID = EMPTY_INT              # 连接编号

        #2018.9.10
        self.request_id = EMPTY_INT              # 请求编号
        self.strategy_id = EMPTY_STRING         # 关联的策略编号

########################################################################
class VtPositionData(VtBaseData):
    """持仓数据类"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        super(VtPositionData, self).__init__()
        
        # 代码编号相关
        self.symbol = EMPTY_STRING              # 合约代码
        self.exchange = EMPTY_STRING            # 交易所代码
        self.vtSymbol = EMPTY_STRING            # 合约在vt系统中的唯一代码，合约代码.交易所代码  
        
        # 持仓相关
        self.direction = EMPTY_STRING           # 持仓方向
        self.position = EMPTY_INT               # 持仓量
        self.frozen = EMPTY_INT                 # 冻结数量
        self.price = EMPTY_FLOAT                # 持仓均价
        self.vtPositionName = EMPTY_STRING      # 持仓在vt系统中的唯一代码，通常是vtSymbol.方向
        self.ydPosition = EMPTY_INT             # 昨持仓
        self.positionProfit = EMPTY_FLOAT       # 持仓盈亏


########################################################################
class VtAccountData(VtBaseData):
    """账户数据类"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        super(VtAccountData, self).__init__()
        
        # 账号代码相关
        self.accountID = EMPTY_STRING           # 账户代码
        self.vtAccountID = EMPTY_STRING         # 账户在vt中的唯一代码，通常是 Gateway名.账户代码
        
        # 数值相关
        self.preBalance = EMPTY_FLOAT           # 昨日账户结算净值
        self.balance = EMPTY_FLOAT              # 账户净值
        self.available = EMPTY_FLOAT            # 可用资金
        self.commission = EMPTY_FLOAT           # 今日手续费
        self.margin = EMPTY_FLOAT               # 保证金占用
        self.closeProfit = EMPTY_FLOAT          # 平仓盈亏
        self.positionProfit = EMPTY_FLOAT       # 持仓盈亏
        

########################################################################
class VtErrorData(VtBaseData):
    """错误数据类"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        super(VtErrorData, self).__init__()
        
        self.errorID = EMPTY_STRING             # 错误代码
        self.errorMsg = EMPTY_UNICODE           # 错误信息
        self.additionalInfo = EMPTY_UNICODE     # 补充信息
        
        self.errorTime = time.strftime('%X', time.localtime())    # 错误生成时间


########################################################################
class VtLogData(VtBaseData):
    """日志数据类"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        super(VtLogData, self).__init__()
        
        self.logTime = time.strftime('%X', time.localtime())    # 日志生成时间
        self.logContent = EMPTY_UNICODE                         # 日志信息
        self.logLevel = INFO                                    # 日志级别


########################################################################
class VtContractData(VtBaseData):
    """合约详细信息类"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        super(VtContractData, self).__init__()
        
        self.symbol = EMPTY_STRING              # 代码
        self.exchange = EMPTY_STRING            # 交易所代码
        self.vtSymbol = EMPTY_STRING            # 合约在vt系统中的唯一代码，通常是 合约代码.交易所代码
        self.name = EMPTY_UNICODE               # 合约中文名
        
        self.productClass = EMPTY_UNICODE       # 合约类型
        self.size = EMPTY_INT                   # 合约大小  合约数量乘数
        self.priceTick = EMPTY_FLOAT            # 合约最小价格 最小变动价位

        # CTP 增加属性
        self.MaxMarketOrderVolume = EMPTY_INT   # 市价单最大下单量
        self.MinMarketOrderVolume = EMPTY_INT   # 市价单最小下单量
        self.MaxLimitOrderVolume =  EMPTY_INT   # 限价单最大下单量
        self.MinLimitOrderVolume = EMPTY_INT    # 限价单最小下单量
        self.LongMarginRatio = EMPTY_FLOAT      # 多头保证金率
        self.ShortMarginRatio = EMPTY_FLOAT     # 空头保证金率
        self.MaxMarginSideAlgorithm = EMPTY_STRING #是否使用大额单边保证金算法  '0' - No , '1' - Yes


        # 期权相关
        self.strikePrice = EMPTY_FLOAT          # 期权行权价
        self.underlyingSymbol = EMPTY_STRING    # 标的物合约代码
        self.optionType = EMPTY_UNICODE         # 期权类型
        self.expiryDate = EMPTY_STRING          # 到期日
        self.last = False    # todo. scott 最后一条记录 query response last-recorder  indicator

        self.marketProduct = EMPTY_STRING       # 交易的产品种类 IF,AU,AG,..




########################################################################
class VtSubscribeReq(object):
    """订阅行情时传入的对象类"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.symbol = EMPTY_STRING              # 代码
        self.exchange = EMPTY_STRING            # 交易所
        self.gatewayName = EMPTY_STRING        # scott
        # 以下为IB相关
        self.productClass = EMPTY_UNICODE       # 合约类型
        self.currency = EMPTY_STRING            # 合约货币
        self.expiry = EMPTY_STRING              # 到期日
        self.strikePrice = EMPTY_FLOAT          # 行权价
        self.optionType = EMPTY_UNICODE         # 期权类型


########################################################################
class VtOrderReq(object):
    """发单时传入的对象类"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.symbol = EMPTY_STRING              # 代码
        self.exchange = EMPTY_STRING            # 交易所
        self.vtSymbol = EMPTY_STRING            # VT合约代码
        self.price = EMPTY_FLOAT                # 价格
        self.volume = EMPTY_INT                 # 数量
    
        self.priceType = EMPTY_STRING           # 价格类型
        self.direction = EMPTY_STRING           # 买卖
        self.offset = EMPTY_STRING              # 开平
        
        # 以下为IB相关
        self.productClass = EMPTY_UNICODE       # 合约类型
        self.currency = EMPTY_STRING            # 合约货币
        self.expiry = EMPTY_STRING              # 到期日
        self.strikePrice = EMPTY_FLOAT          # 行权价
        self.optionType = EMPTY_UNICODE         # 期权类型     
        self.lastTradeDateOrContractMonth = EMPTY_STRING   # 合约月,IB专用
        self.multiplier = EMPTY_STRING                     # 乘数,IB专用

        #
        self.request_id = EMPTY_INT             # 发单请求编号
        self.strategy_id = EMPTY_STRING         # 策略编号
        

########################################################################
class VtCancelOrderReq(object):
    """撤单时传入的对象类"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.symbol = EMPTY_STRING              # 代码
        self.exchange = EMPTY_STRING            # 交易所
        self.vtSymbol = EMPTY_STRING            # VT合约代码
        
        # 以下字段主要和CTP、LTS类接口相关
        self.orderID = EMPTY_STRING             # 报单号
        self.frontID = EMPTY_STRING             # 前置机号
        self.sessionID = EMPTY_STRING           # 会话号

        #
        self.request_id = EMPTY_INT  # 发单请求编号
        self.strategy_id = EMPTY_STRING  # 策略编号

########################################################################
class VtSingleton(type):
    """
    单例，应用方式:静态变量 __metaclass__ = Singleton
    """
    
    _instances = {}

    #----------------------------------------------------------------------
    def __call__(cls, *args, **kwargs):
        """调用"""
        if cls not in cls._instances:
            cls._instances[cls] = super(VtSingleton, cls).__call__(*args, **kwargs)
            
        return cls._instances[cls]
    
    
class VtDepthMarketQueryReq(object):
    def __init__(self):
        self.symbol = EMPTY_STRING              # 代码
        self.exchange = EMPTY_STRING            # 交易所
        self.request_id = EMPTY_INT

class VtDepthMarketData(object):
    """合约深度行情数据，包含：最高、最低价"""
    def __init__(self):
        self.symbol = EMPTY_STRING              # 代码
        self.exchange = EMPTY_STRING            # 交易所
        self.vtSymbol = EMPTY_STRING            # VT合约代码

        self.LastPrice = EMPTY_FLOAT            # 最新价
        self.PreSettlementPrice = EMPTY_FLOAT   # 上次结算价

        #昨收盘
        self.PreClosePrice = EMPTY_FLOAT
        #昨持仓量
        self.PreOpenInterest = EMPTY_INT
        #今开盘
        self.OpenPrice = EMPTY_FLOAT
        #最高价
        self.HighestPrice  = EMPTY_FLOAT
        #最低价
        self.LowestPrice = EMPTY_FLOAT
        #数量
        self.Volume = EMPTY_INT
        #成交金额
        self.Turnover  = EMPTY_FLOAT
        #持仓量
        self.OpenInterest = EMPTY_INT
        #今收盘
        self.ClosePrice  = EMPTY_FLOAT
        #本次结算价
        self.SettlementPrice  = EMPTY_FLOAT
        #涨停板价
        self.UpperLimitPrice  = EMPTY_FLOAT
        #跌停板价
        self.LowerLimitPrice  = EMPTY_FLOAT
        #昨虚实度
        self.PreDelta  = EMPTY_FLOAT
        #今虚实度
        self.CurrDelta  = EMPTY_FLOAT
        #最后修改时间
        self.UpdateTime  = EMPTY_STRING
        #最后修改毫秒
        self.UpdateMillisec = EMPTY_INT
        #当日均价
        self.AveragePrice = EMPTY_FLOAT
        #业务日期
        self.ActionDay  = EMPTY_STRING

class VtContractCommissionRateQueryReq(object):
    """合约交易手续费"""
    def __init__(self):
        self.symbol = EMPTY_STRING              # 代码
        self.exchange = EMPTY_STRING            # 交易所
        self.broker_id = EMPTY_STRING
        self.investor_id = EMPTY_STRING
        self.request_id = EMPTY_INT

########################################################################
class VtContractCommissionRateData(VtBaseData):
    """合约手续费率"""
    def __init__(self):
        """Constructor"""
        super(VtContractCommissionRateData, self).__init__()
        self.symbol = EMPTY_STRING          # 代码
        self.OpenRatioByMoney = EMPTY_FLOAT # 开仓手续费率
        self.OpenRatioByVolume = EMPTY_FLOAT # 开仓手续费
        self.CloseRatioByMoney = EMPTY_FLOAT # 平仓手续费率
        self.CloseRatioByVolume = EMPTY_FLOAT # 平仓手续费
        self.CloseTodayRatioByMoney = EMPTY_FLOAT # 平今手续费率
        self.CloseTodayRatioByVolume = EMPTY_FLOAT # 平今手续费
        self.exchange = EMPTY_STRING      # 交易所代码

        self.last = False