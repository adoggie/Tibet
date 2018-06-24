# coding: utf-8


import json
from uuid import uuid4
from collections import OrderedDict
from mantis.fundamental.application.app import instance
from mantis.fundamental.utils.useful import singleton

from mantis.trade.types import ProductClass, TickData, BarData, TimeDuration
from mantis.trade.types import FutureTradeCommand
from mantis.trade.message import Request, RequestOrResponse, Response
from mantis.trade.constants import *


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

    def keepalive_trade_adapter(self, timer):
        pass

    def addAccount(self, quota):
        pass


class FutureHandler(ProductHandler):
    """
    期货处理器
    """

    def __init__(self, controller):
        ProductHandler.__init__(self)
        self.type = ProductClass.Future
        self.controller = controller
        self.chans = set()
        self.accounts = OrderedDict()  # 持有的账户信息（配额限定)
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
        from mantis.trade.constants import CommandChannelTradeAdapterREAD, CommandChannelTradeAdapterWRITE, \
            TradeAdapterServiceIdFormat
        broker = instance.messageBrokerManager.get('redis')

        account = TradeAdapterServiceIdFormat.format(product=quota.product, account=quota.account)
        key = CommandChannelTradeAdapterREAD.format(account=account)
        write = broker.createPubsubChannel(key)  # 初始化交易适配器的消息投递通道

        key = CommandChannelTradeAdapterWRITE.format(account=account)
        read = broker.createPubsubChannel(key, self._handle_trade_message)

        quota.channels = {'read': read, 'write': write}

        self.chans.add(read)
        self.chans.add(write)
        read.open()
        write.open()

        self.accounts[quota.account] = quota

        if not self.default_account:
            self.set_default_account(quota.account)  # 设置为默认账号

    def keepalive_trade_adapter(self, timer):
        for quota in self.accounts.values():
            channel = quota.channels.get('write')
            # 发送保活消息
            msg = Request(name=SystemCommand.KeepAlive)
            channel.publish_or_produce(msg.marshall())
            print 'Send keep alive message to Trade Adapter..\n', msg.marshall()

    def _handle_trade_message(self, data, ctx):
        """处理从资金接入适配器返回的消息 """
        channel = ctx['channel']
        message = RequestOrResponse.parse(data)
        if not message:
            return
        if isinstance(message, Response):
            self._process_message_response(message)

    def _process_message_response(self, message):
        if message.header.get('ref_id') != self.uuid:  # 并不是自己发送的响应消息
            print 'Response Message: <{}> , I do not care.'.format(message.ref_id)
            return

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
        chan = broker.createPubsubChannel(key, self._handle_tick)
        self.chans.add(chan)
        chan.open()
        chan.props['symbol'] = symbol
        chan.props['gateway'] = gateway
        chan.props['handler'] = self

    def _handle_tick(self, message, ctx):
        chan = ctx.get('channel')
        data = TickData()
        data.data = message
        data.symbol = chan.props.get('symbol')
        data.gateway = chan.props.get('gateway')
        data.handler = self
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
        chan = broker.createPubsubChannel(subkey, self._handle_bar)
        self.chans.add(chan)
        chan.open()
        chan.props['symbol'] = symbol
        chan.props['scale'] = scale
        chan.props['gateway'] = gateway
        chan.props['handler'] = self

    def _handle_bar(self, message, ctx):
        chan = ctx.get('channel')
        data = BarData()
        data.data = message
        data.symbol = chan.props.get('symbol')
        data.scale = chan.props.get('scale')
        data.gateway = chan.props.get('gateway')
        data.handler = self
        data.product = self.type
        self.controller.onBar(data)

    def sell(self, price, volume, stop=False, account=''):
        """卖平"""
        return self.sendOrder(FutureTradeCommand.ORDER_SELL, price, volume, stop, account)

        # ----------------------------------------------------------------------

    def short(self, price, volume, stop=False, account=''):
        """卖开"""
        return self.sendOrder(FutureTradeCommand.ORDER_SHORT, price, volume, stop, account)

        # ----------------------------------------------------------------------

    def cover(self, price, volume, stop=False, account=''):
        """买平"""
        return self.sendOrder(FutureTradeCommand.ORDER_COVER, price, volume, stop, account)

        # ----------------------------------------------------------------------

    def sendMessage(self, quota, request):
        """

        :param quota:  配额资金账户
        :param request_or_response: 请求/响应消息
        :return:
        """
        request.header['ref_id'] = self.uuid
        message = request.marshall()

        channel = quota.channels.get('write')
        channel.publish_or_produce(message)

    def sendOrder(self, orderType, price, volume, stop=False, account=''):
        """
        发送订单到指定的队列
        :param orderType: FutureOrderCommand
        :param price:
        :param volume:
        :param stop:
        :param account:
        :return:
        """
        """发送委托"""
        if not account:
            if self.default_account:
                account = self.default_account
            else:
                return False

        quota = self.accounts.get(account)  # TradeAccountQuota
        if not quota:
            return False

        # 将委托发送到指定的 redis 队列上
        body = OrderedDict(product=quota.product, account=account, price=price, volume=volume, stop=stop)
        request = Request(name=orderType, data=body)

        self.sendMessage(quota, request)

        # if self.trading:
        #     # 如果stop为True，则意味着发本地停止单
        #     if stop:
        #         vtOrderIDList = self.ctaEngine.sendStopOrder(self.vtSymbol, orderType, price, volume, self)
        #     else:
        #         vtOrderIDList = self.ctaEngine.sendOrder(self.vtSymbol, orderType, price, volume, self)
        #     return vtOrderIDList
        # else:
        #     # 交易停止时发单返回空字符串
        #     return []

        # ----------------------------------------------------------------------

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
