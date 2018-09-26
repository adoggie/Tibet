#coding:utf-8

from proxy import *


def test_trade_adapter_proxy():
    proxy = TradeAdapterProxy('http://127.0.0.1:18900/v1/message/')
    # data = proxy.getOrder('001')
    print '-- getCurrentAccount() --'
    print proxy.getCurrentAccount().__dict__
    print '-- getAllPositions() --'
    for pos in proxy.getAllPositions():
        print pos.__dict__

    print '-- getAllWorkingOrders() -- '
    for order in proxy.getAllWorkingOrders():
        print order.__dict__

    print '-- getAllTrades() -- '
    for trade in proxy.getAllTrades():
        print trade.__dict__

def test_send_order():
    pass


if __name__ == '__main__':
    test_trade_adapter_proxy()