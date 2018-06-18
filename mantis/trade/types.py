# coding:utf-8

from mantis.fundamental.utils.useful import hash_object,object_assign
from mantis.fundamental.basetype import ValueEntry

class ServiceType(object):
    UnDefined           = ValueEntry('undefined',u'未定义')
    GlobalDispatcher    = ValueEntry('dispatcher',u'调度服务器')
    MarketAdapter       = ValueEntry('market_adapter',u'行情适配器')
    TradeAdapter        = ValueEntry('trade_adapter',u'交易适配器')
    TradeServer         = ValueEntry('trade_server',u'交易服务器')
    DataResourceServer  = ValueEntry('data_res_server',u'数据资源服务器')
    DataPAServer        = ValueEntry('data_pa_server',u'数据处理和分析服务')
    StrategyRunner      = ValueEntry('strategy_runner',u'策略容器')
    StrategyDevRunner      = ValueEntry('strategy_dev_runner',u'策略容器')
    StrategyLauncher    = ValueEntry('strategy_launcher',u'策略加载器')
    FrontLauncher       = ValueEntry('front_launcher',u'前端服务加载器,负责交易/行情适配器的加载')


class TimeDuration(object):
    SECOND     = 1
    MINUTE     = SECOND * 60
    HOUR       = MINUTE * 60
    MINUTE_1   = MINUTE
    MINUTE_5   = MINUTE * 5
    MINUTE_15  = MINUTE * 15
    MINUTE_30  = MINUTE * 30
    HOUR_1     = HOUR
    DAY        = HOUR * 24
    SCALES ={
        '1m':MINUTE_1,
        '5m':MINUTE_5,
        '15m':MINUTE_15,
        '30m':MINUTE_30,
        '1h':HOUR_1,
        '1d':DAY
    }

TimeScale = TimeDuration

class ProductClass(object):
    Undefined = ValueEntry('undefined',u'undefined')
    Future  = ValueEntry('future',u'期货')
    Stock   = ValueEntry('stock',u'股票')



class TradeAccountInfo(object):
    """
    交易资金账户信息
    """
    NAME ='trade_account'
    def __init__(self):
        self.product_class = ''     # 产品类型 :  期货/股票
        self.exchange = ''
        self.gateway = ''           # 交易接入系统名称 CTP
        self.broker = ''            # 经纪公司
        self.user = ''
        self.password = ''
        self.market_server_addr = ''
        self.trade_server_addr = ''

        self.auth_code = ''
        self.user_product_info = ''

    # def update(self,cfgs,prefix=''):
    #     if prefix :
    #         prefix+='.'
    #     prefix+=TradeAccountInfo.NAME+'.'
    #     self.product_class  = cfgs.get(prefix+'product_class','')
    #     self.exchange       = cfgs.get(prefix+'exchange','')
    #     self.gateway        = cfgs.get(prefix+'gateway','')
    #     self.broker         = cfgs.get(prefix+'broker','')
    #     self.user           = cfgs.get(prefix+'user','')
    #     self.password       = cfgs.get(prefix+'password','')
    #     self.market_server_addr       = cfgs.get(prefix+'market_server_addr','')
    #     self.trade_server_addr       = cfgs.get(prefix+'trade_server_addr','')
    #     self.auth_code       = cfgs.get(prefix+'auth_code','')
    #     self.user_product_info       = cfgs.get(prefix+'user_product_info','')
    #
    # def dict(self,prefix=''):
    #     if prefix:
    #         prefix+='.'
    #     prefix+=TradeSubAccountInfo.NAME+'.'
    #     return hash_object(self,key_prefix=prefix,excludes=['NAME'])

    def loads(self,cfgs):
        object_assign(self,cfgs)

    def dumps(self):
        return hash_object(self)

USER_NAME_UNDEFINED = ''

class TradeSubAccountInfo(object):
    """
    交易开户资金子账户(系统内交易账户）
    """
    NAME = 'trade_sub_account'
    def __init__(self):
        self.account = ''
        self.fund_limit = 0 # max fund quota for trade user

    # def update(self,cfgs,prefix=''):
    #     if prefix :
    #         prefix+='.'
    #     prefix+=TradeSubAccountInfo.NAME + '.'
    #     self.account  = cfgs.get(prefix+'account','')
    #     self.fund_limit  = cfgs.get(prefix+'fund_limit',0)
    #
    # def dict(self,prefix=''):
    #     if prefix:
    #         prefix+='.'
    #     prefix+=TradeSubAccountInfo.NAME+'.'
    #     return hash_object(self,prefix,excludes=['NAME'])

    def loads(self, cfgs):
        object_assign(self,cfgs)

    def dumps(self):
        result = hash_object(self)
        return result


class TradeUserInfo(object):
    NAME = 'trade_user'
    def __init__(self):
        self.user = ''
        self.password = ''


    # def update(self,cfgs,prefix=''):
    #     if prefix :
    #         prefix+='.'
    #     prefix+=TradeUserInfo.NAME + '.'
    #     self.user  = cfgs.get(prefix+'user','')
    #     self.password  = cfgs.get(prefix+'password',0)
    #
    # def dict(self,prefix=''):
    #     if prefix:
    #         prefix+='.'
    #     prefix+=TradeUserInfo.NAME+'.'
    #     return hash_object(self,prefix,excludes=['NAME'])

    def loads(self, cfgs):
        object_assign(self,cfgs)

    def dumps(self):
        result = hash_object(self)
        return result


class TickData(object):
    def __init__(self):
        self.symbol = ''
        self.data = {}
        self.gateway = ''

class BarData(object):
    def __init__(self):
        self.data = {}
        self.symbol = ''
        self.scale = '' # 1m,5m,..,1h,1d...
        self.gateway =''


