# coding: utf-8


import json
from uuid import uuid4
from collections import OrderedDict
from mantis.trade.types import ServiceType
from mantis.trade.message import Request, Message
from mantis.trade.constants import *
from vnpy.trader.vtObject import *
from vnpy.trader.vtConstant import *
from vnpy.trader.app.ctaStrategy.ctaBase import *
from mantis.trade import command
from proxy import *

class ProductHandler(object):
    NONE = None

    def __init__(self):
        self.type = ProductClass.Undefined
        self.uuid = uuid4().hex
        self.controller = None

    def open(self):
        raise NotImplemented

    def close(self):
        raise NotImplemented

    def startKeepAliveWithTradeAdapter(self):
        self.controller.setTimer(action=self.keepalive_trade_adapter, timeout=2)

class FutureHandler(ProductHandler):
    """
    期货处理器
    """

    def __init__(self, controller):
        ProductHandler.__init__(self)
        self.type = ProductClass.Future
        self.controller = controller
        self.chans = set()              # sub - 订阅对方系统发布的消息
        self.accounts = OrderedDict()   # 持有的账户信息（配额限定)
        self.default_account = ''
        self.service = controller.service

    def open(self):
        self.startKeepAliveWithTradeAdapter()

    def close(self):
        for chan in self.chans:
            chan.close()

    def addAccount(self, quota):
        """
        添加账户
        准备消息发送和接收通道 ( 双向 )
        :param account: TradeAccountQuota
        :return:
        """
        # broker = instance.messageBrokerManager.get('redis')
        service_id = TradeAdapterServiceIdFormat.format(product=quota.product, account=quota.account)

        # 在adapter的广播地址上接收消息
        #
        address_pub = ServiceCommandChannelAddressPub.format(service_id=service_id, service_type=ServiceType.TradeAdapter)
        read = self.service.createServiceCommandChannel(address_pub,self.handle_message)
        read.props['quota']  = quota

        address_sub = ServiceCommandChannelAddressSub.format(service_id=service_id, service_type=ServiceType.TradeAdapter)
        write = self.service.createServiceCommandChannel(address_sub, open=True)

        quota.channels = {'read': read,'write':write}
        self.chans.add(read)
        self.chans.add(write)

        self.accounts[quota.account] = quota

        if not self.default_account:
            self.set_default_account(quota.account)  # 设置为默认账号

    def keepalive_trade_adapter(self, timer):
        """保持trade-adapter的连接，迫使trade-adapter保持在线"""

        for quota in self.accounts.values():
            channel = quota.channels.get('write')   # 交易适配器的接收通道
            # 发送保活消息
            msg = Message(command.KeepAlive.NAME)
            Request(channel).send(msg)
            print 'Send keep alive message to Trade Adapter..\n', msg.marshall()

    def handle_message(self, data, ctx):
        """处理从资金接入适配器返回的消息 """
        channel = ctx['channel']
        message = Message.unmarshall(data)
        if not message:
            return

        if message.name == command.OnAccountData.NAME:
            account = VtAccountData()
            account.__dict__ = message.data

        if message.name == command.ServiceStatusBroadcast.NAME:
            data = command.ServiceStatusBroadcast()
            data.__dict__ = message.data
            quota = channel.props.get('quota')
            if not quota.trade_proxy: # 未定义
                quota.trade_proxy = TradeAdapterProxy(data.http)


    def set_default_account(self, name):
        self.default_account = name

    def subTicks(self, symbol, gateway='ctp'):
        """
        订阅行情Tick数据
        从redis的pubsub中订阅指定的产品
        """
        key = self.service.getConfig().get('future_tick_sub_key')
        key = key.format(gateway=gateway, symbol=symbol)
        broker = instance.messageBrokerManager.get('redis')
        chan = broker.createPubsubChannel(key, self.handle_tick)
        self.chans.add(chan)
        chan.open()

    def handle_tick(self, message, ctx):
        chan = ctx.get('channel')
        data = VtTickData()
        data.__dict__ = message
        data.product = self.type
        self.controller.onTick(data)

    def subBars(self, symbol, scale, gateway='ctp'):
        """
        订阅指定类型的k线数据
        """
        scale = scale.lower()
        gateway = gateway.lower()
        if scale not in TimeDuration.SCALES.keys():
            return False

        subkey = self.service.getConfig().get('future_bar_sub_key')
        subkey = subkey.format(gateway=gateway, symbol=symbol, scale=scale)

        broker = instance.messageBrokerManager.get('redis')
        chan = broker.createPubsubChannel(subkey, self.handle_bar)
        self.chans.add(chan)
        chan.open()
        chan.props['scale'] = scale


    def handle_bar(self, message, ctx):
        chan = ctx.get('channel')
        data = VtBarData()
        data.__dict__ = message
        data.scale = chan.props.get('scale')
        data.product = self.type
        self.controller.onBar(data)

    def buy(self, price, volume, stop=False, account=''):
        """买开"""
        return self.sendOrder(CTAORDER_BUY, price, volume, stop, account)


    def sell(self, price, volume, stop=False, account=''):
        """卖平"""
        return self.sendOrder(CTAORDER_SELL, price, volume, stop, account)

        # ----------------------------------------------------------------------

    def short(self, price, volume, stop=False, account=''):
        """卖开"""
        return self.sendOrder(CTAORDER_SHORT, price, volume, stop, account)

        # ----------------------------------------------------------------------

    def cover(self, price, volume, stop=False, account=''):
        """买平"""
        return self.sendOrder(CTAORDER_COVER, price, volume, stop, account)

    def roundToPriceTick(self, priceTick, price):
        """取整价格到合约最小价格变动"""
        if not priceTick:
            return price

        newPrice = round(price / priceTick, 0) * priceTick
        return newPrice

        # ----------------------------------------------------------------------
    def sendOrder(self, vtSymbol, orderType, price, volume, account=''):
        """发单"""
        from mantis.trade.utils import get_contract_detail

        # contract = self.mainEngine.getContract(vtSymbol)
        if not account:
            account = self.default_account
        quota = self.accounts.get(account)
        # 交易适配服务未准备好，拒绝下单
        if not quota or not quota.trade_proxy:
            return []

        # channel = quota.channels.get('sub')

        contract = VtContractData()
        contract.__dict__ = get_contract_detail(vtSymbol)

        req = VtOrderReq()
        req.symbol = contract.symbol
        req.exchange = contract.exchange
        req.vtSymbol = contract.vtSymbol
        req.price = self.roundToPriceTick(contract.priceTick, price)
        req.volume = volume

        # req.productClass = strategy.productClass
        # req.currency = strategy.currency

        # 设计为CTA引擎发出的委托只允许使用限价单
        req.priceType = PRICETYPE_LIMITPRICE

        # CTA委托类型映射
        if orderType == CTAORDER_BUY:
            req.direction = DIRECTION_LONG
            req.offset = OFFSET_OPEN

        elif orderType == CTAORDER_SELL:
            req.direction = DIRECTION_SHORT
            req.offset = OFFSET_CLOSE

        elif orderType == CTAORDER_SHORT:
            req.direction = DIRECTION_SHORT
            req.offset = OFFSET_OPEN

        elif orderType == CTAORDER_COVER:
            req.direction = DIRECTION_LONG
            req.offset = OFFSET_CLOSE

        req = command.OrderRequest()
        return quota.trade_proxy.sendOrder(req,self.service.service_id)


        # 一下操作进行拆单动作，形成多个订单请求，批量发送
        # 在这里不操作，由 TradeAdapter服务进行拆单

        # 委托转换
        # reqList = self.mainEngine.convertOrderReq(req)
        # vtOrderIDList = []
        #
        # if not reqList:
        #     return vtOrderIDList
        #
        # for convertedReq in reqList:
        #     vtOrderID = self.mainEngine.sendOrder(convertedReq, contract.gatewayName)  # 发单
        #     self.orderStrategyDict[vtOrderID] = strategy  # 保存vtOrderID和策略的映射关系
        #     self.strategyOrderDict[strategy.name].add(vtOrderID)  # 添加到策略委托号集合中
        #     vtOrderIDList.append(vtOrderID)
        #
        # self.writeCtaLog(u'策略%s发送委托，%s，%s，%s@%s'
        #                  % (strategy.name, vtSymbol, req.direction, volume, price))
        #
        # return vtOrderIDList


    def cancelOrder(self, vtOrderID):
        """撤单"""
        # 如果发单号为空字符串，则不进行后续操作
        if not vtOrderID:
            return

        if STOPORDERPREFIX in vtOrderID:
            self.ctaEngine.cancelStopOrder(vtOrderID)
        else:
            self.ctaEngine.cancelOrder(vtOrderID)

        # ----------------------------------------------------------------------

    def cancelAll(self):
        """全部撤单"""
        self.ctaEngine.cancelAll(self.name)

    def loadTick(self, symbol, days=1, limit=0, product_class=ProductClass.Future):
        """读取tick数据
        向 DataResService 发起 http 查询请求
        :param symbol: 合约代码
        :param days:  距今天数
        :param limit: 最大的bar数量 , 0: 未限制

        直接连接到mongodb 读取tick数据
        """
        # return DataResServiceProxy().queryTicks(symbol, days, limit, product_class)
        pass
        # ----------------------------------------------------------------------

    def loadBar(self, symbol, scale, days=1, limit=0, product_class=ProductClass.Future):
        """读取bar数据
        :param symbol: 合约代码
        :param scale : bar时间宽度 1m,5m,15m,..
        :param days:  距今天数
        :param limit: 最大的bar数量 , 0: 未限制
        """
        # return DataResServiceProxy().queryBars(symbol, days, limit, product_class)
        pass


class StockHandler(ProductHandler):
    """
    股票处理器
    """
    def __init__(self, controller):
        ProductHandler.__init__(self)
        self.type = ProductClass.Stock
        self.controller = controller

    def open(self):
        pass
