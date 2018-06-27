# coding:utf-8

# CommandChannelTradeAdapterGet   = 'trade.command.channel.adapters.{account}.read' # 交易适配器接收通道
# CommandChannelTradeAdapterWRITE  = 'trade.command.channel.adapters.{account}.write'   # 策略运行器接收通道 （广播接收)

#服务程序的命令接收和发送消息的通道地址
ServiceCommandChannelAddressGet = 'redis/trade.command.channel.{service_type}.{service_id}.get/queue'
ServiceCommandChannelAddressSub = 'redis/trade.command.channel.{service_type}.{service_id}.sub/pubsub'

ServiceCommandChannelAddressPut = 'redis/trade.command.channel.{service_type}.{service_id}.put/queue'
ServiceCommandChannelAddressPub = 'redis/trade.command.channel.{service_type}.{service_id}.pub/pubsub'


CommandChannelTradeAdapterLauncherSub = 'redis/trade.command.channel.adapter.launcher.sub/pubsub'  # 适配器加载器的消息接收通道

TradeAdapterServiceIdFormat = '{product}.{account}' # 交易适配器服务ID的命名格式

ServiceKeepAlivedTime = 5   # 指定时间内必须保活，否则视为离线

DevelopAccountNameFormat    = "development.accounts.{product}.{account}"
TradeAccountNameFormat      = "trade.accounts.{product}.{account}"
DevelopUserAccountQuotaFormat = "development.users.{user}.quotas.{account}"
TradeUserAccountQuotaFormat = "trade.users.{user}.quotas.{account}"


DevelopUserStrategyKeyPrefix ='development.users.{user}.strategies.{strategy_name}'
TradeUserStrategyKeyPrefix = 'trade.users.{user}.strategies.{strategy_name}'

CTAContractListKey = 'cta_contract_list'


class StrategyRunMode(object):
    Null        = 'null'
    Development = 'dev'
    Product     = 'product'
