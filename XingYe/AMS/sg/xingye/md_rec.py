#coding:utf-8

"""
md_rec.py
日行情记录程序
记录指定股票日内 分时、各K线数据

"""
from utils.useful import hash_object
from functools import partial
import stbase
import simple_st



context = None
print_line = stbase.TradeManager().print_line
def init():
    tm = stbase.TradeManager().init(context,logpath='z:/ams/md',strategy_name='md_rec',market_data_save=True)

    codes=['1000001','1300252','1300310','1300025',
           '0600000','1300638','1300504','0601162']

    # stock = tm.addStock('0600000')
    # stock = tm.addStock('1300310') #宜通世纪
    stocks = []
    for code in codes:
        stock = tm.addStock(code)
        stocks.append(stock)



'''
（1）交易端首页登录账号/密码：zssp000/xyzq601377；
其现货资金账号/密码：30073627/112233

兴业-云服务器账号
================
账号：XYXY001
密码：XYXY0000
'''