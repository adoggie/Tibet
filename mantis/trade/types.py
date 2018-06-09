# coding:utf-8

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
    StrategyLauncher    = ValueEntry('strategy_launcher',u'策略加载器')
    FrontLauncher       = ValueEntry('front_launcher',u'前端服务加载器,负责交易/行情适配器的加载')
