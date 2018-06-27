# coding: utf-8

from vnpy.trader.vtObject import *

# class Command(object):
#     def __init__(self,name):
#         self.name = name

class StartTradeAdapter(object):
    NAME = 'start_trade_adapter'
    def __init__(self):
        pass

class KeepAlive(object):
    NAME = 'keepalive'
    def __init__(self):
        pass

class ServiceStatusBroadcast(object):
    NAME = 'service_status_broadcast'
    def __init__(self):
        self.service_id = ''
        self.service_type =  ''
        self.http = ''

class OrderRequest(VtOrderReq):
    NAME = 'order_request'

class OrderCancel(VtCancelOrderReq):
    NAME = 'order_cancel'

# class StopOrderRequest(Vt)
class OnPositionData(VtPositionData):
    NAME = 'on_position_data'

class OnOrderData(VtOrderData):
    NAME = 'on_order_data'

class OnTradeData(VtTradeData):
    NAME = 'on_trade_data'


class OnAccountData(VtAccountData):
    NAME = 'on_account_data'


class GetOrder(object):
    NAME = 'get_order'
    def __init__(self):
        self.order_id = ''

    class Result(object):
        def __init__(self):
            self.order = VtOrderData()

        def assign(self,result):
            self.order.__dict__ = result

class GetAllWorkingOrders(object):
    NAME = 'get_all_working_orders'
    def __init__(self):
        pass

    class Result(object):
        def __init__(self):
            self.orders = []

        def assign(self,result):
            for r in result:
                order = VtOrderData()
                order.__dict__ = r
                self.orders.append(order)

class GetAllOrders(GetAllWorkingOrders):
    NAME = 'get_all_orders'
    def __init__(self):
        GetAllWorkingOrders.__init__(self)


class GetAllTrades(object):
    NAME = 'get_all_trades'
    def __init__(self):
        pass

    class Result(object):
        def __init__(self):
            self.trades = []

        def assign(self,result):
            for r in result:
                trade = VtTradeData()
                trade.__dict__ = r
                self.trades.append(trade)

class GetAllPositions(object):
    NAME = 'get_all_positions'
    def __init__(self):
        pass

    class Result(object):
        def __init__(self):
            self.positions = []

        def assign(self,result):
            for r in result:
                pos = VtPositionData()
                pos.__dict__ = r
                self.positions.append(pos)

class GetAllAccounts(object):
    NAME = 'get_all_accounts'
    def __init__(self):
        pass

    class Result(object):
        def __init__(self):
            self.accounts = []

        def assign(self,result):
            for r in result:
                account = VtAccountData()
                account.__dict__ = r
                self.accounts.append(account)










