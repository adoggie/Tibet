#coding:utf-8

from proxy import *


def test_trade_adapter_proxy():
    proxy = TradeAdapterProxy('http://172.16.109.133:18900/v1/message/')
    data = proxy.getOrder('001')
    print data

if __name__ == '__main__':
    test_trade_adapter_proxy()