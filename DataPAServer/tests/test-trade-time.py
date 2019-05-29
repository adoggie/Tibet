#coding:utf-8

from mantis.trade.trade_time import get_trade_timespace_by_product,\
    get_trade_timespace_by_exchange,is_trade_day

print get_trade_timespace_by_product('A')
print get_trade_timespace_by_exchange('sf_1')
print is_trade_day('A','2018-9-23')