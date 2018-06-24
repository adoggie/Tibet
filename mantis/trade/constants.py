# coding:utf-8

CommandChannelTradeAdapterREAD   = 'trade.command.channel.adapters.{account}.read' # 交易适配器接收通道
CommandChannelTradeAdapterWRITE  = 'trade.command.channel.adapters.{account}.write'   # 策略运行器接收通道 （广播接收)

CommandChannelTradeAdapterLauncherREAD = 'trade.command.channel.adapter.launcher.read'  # 适配器加载器的消息接收通道

TradeAdapterServiceIdFormat = '{product}_{account}' # 交易适配器服务ID的命名格式

ServiceKeepAlivedTime = 5   # 指定时间内必须保活，否则视为离线

DevelopAccountNameFormat    = "development.accounts.{product}.{name}"
TradeAccountNameFormat      = "trade.accounts.{product}.{name}"
DevelopUserAccountQuotaFormat = "development.users.{user}.quotas.{name}"
TradeUserAccountQuotaFormat = "trade.users.{user}.quotas.{name}"


DevelopUserStrategyKeyPrefix ='development.users.{user}.strategies.{strategy_name}'
TradeUserStrategyKeyPrefix = 'trade.users.{user}.strategies.{strategy_name}'


class SystemCommand(object):
    StartTradeAdapter = 'start_trade_adapter'
    KeepAlive         = 'keepalive'     # 要求系统存活