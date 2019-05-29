#coding:utf-8


"""
pip install tushare==1.2.10 simplejson

-- 单独运行simple_st.py 需添加如下环境变量
export LD_LIBRARY_PATH=/opt/kungfu/master/lib/yijinjing:/opt/kungfu/toolchain/boost-1.62.0/lib
export PYTHONPATH=/opt/kungfu/master/lib/wingchun
"""
import json
import numpy as np
import pandas as pa
import talib as ta
import stbase
import time
import datetime

from utils.useful import hash_object
from utils.useful import singleton

import ts_get

CODE ='000001'
STOCK_LIST = [CODE]


def filter_trade_time(k):
    end = k['EndUpdateTime']
    tm = time.strptime(end,'%H:%M:%S')
    a = time.strptime('11:30:00','%H:%M:%S')
    b = time.strptime('13:00:00','%H:%M:%S')
    c = time.strptime('15:00:00','%H:%M:%S')

    if tm > a and tm < b :
        return False
    return True

def get_bars(code,interval,nbar=50):
    """
    当天的k线不够则从tushare中获取

    tushare.pro版本开源版本不提供除了日线之外的k线， 中泰流程开通可以提供

    tushare老版本 可查询除了昨日之外的历史分钟线

        ts.get_hist_data('000001',start='2019-01-09',end='2019-01-09',ktype='5')

    :param code: 股票代码
    :param interval: k线类型
    :param bar_num:  k线数量
    :return:
    """
    bars = []
    f = open('{}-{}.txt'.format(code, interval))
    lines = filter(lambda _:_ and _[0]!='#', map(str.strip,f.readlines()) )

    f.close()
    lines = map(lambda _:json.loads(_),lines)
    lines = map(lambda _:_['Close'],lines)
    # print lines
    # lines = lines[:max]
    lines = lines[::-1]
    lines = filter(filter_trade_time,lines)
    close = np.array(lines)

    if len(close) < nbar :
        more = nbar - len(close)
        # 读取历史k线
        start = datetime.datetime.now() - datetime.timedelta(days=20)
        start = start.strftime('%Y%m%d')
        end = datetime.datetime.now()
        end = end.strftime('%Y%m%d')

        # 收费接口(ZTS)
        # df = ts_get.pro_bar(ts_code=code, start_date=start, end_date=end,freq=str(interval)+'MIN')
        df = ts_get.get_hist_data(code,start=start,end=start, ktype=str(interval)) # 普通版本（无昨日k线)

        close2 = df.head(more).close.values
        close = np.append(close, close2)


    # df = ts.get_hist_data(code, ktype='5')
    # close2 = df.close.values
    # close = np.append(close,close2)

    return close


def strategy_exec_bar(bars, intervals,source, rcv_time):
    """K线触发策略计算
    """
    for code, bar in bars.items():
        print code,bar
        # print hash_object(bar )
        if code == CODE : # and intervals == 5:
            strategy_ma(code)
            # strategy_inday(code,bar)

def strategy_ma( code=CODE ,interval = 5):
    """计算均线策略"""
    close = get_bars(code, interval)
    print 'size:',len(close)
    # print close
    # nbar = interval

    a,b = ta.MA(close, 5)[-2:]

    c,d = ta.MA(close, 10)[-2:]


    if b >= d and a< c:
        num = 100
        amount = stbase.TradeManeager().kf_proxy.get_ammount()
        last_price = stbase.TradeManager().getStock(code).last_price
        cost = last_price * num
        if cost <= amount * 0.1:
            stbase.TradeManager().kf_proxy.buy(code,num)
    if b <=d and a > c:
        num  = 100
        if num <= stbase.TradeManager().getStock(code).pos.net_yd:
            stbase.TradeManager().kf_proxy.sell(code,num)


def strategy_inday(code,bar,num = 100 ,limit=0.02 ):
    """日内涨跌幅策略
    @:param code: 股票代码
    @:param num ：买卖数量
    @:param limit: 价格浮动限
    """
    stock = stbase.TradeManager().getStock(code)

    zf =  stock.last_price / stock.yesterday_close_price - 1
    if zf <= -limit:
        #跌幅过限
        amount = stbase.TradeManager().kf_proxy.get_ammount()
        pos_sum = stock.pos.net_total

        if stock.last_price *pos_sum <= amount * 0.1:
            """持仓资金占总资金 <= 10% """
            stbase.TradeManager().kf_proxy.buy(code,num)
    elif zf >= limit:
        if stock.pos.net_total >= num:
            stbase.TradeManager().kf_proxy.sell(code,num)


if __name__ == '__main__':
    # print api.daily(ts_code='000001.SZ',trade_date='20190104')
    strategy_ma(CODE)
