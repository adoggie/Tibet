#coding:utf-8

import pandas as pd
import numpy as np
from datetime import datetime as DateTime, time as Time
from dateutil.parser import parse
from dateutil.rrule import *
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.pylab import date2num
# import matplotlib.finance as mpf
# import mpl_finance as mpf
import  matplotlib.finance as  mpf
# % matplotlib inline

import pymongo

conn = pymongo.MongoClient('localhost', 27018)


# conn = pymongo.MongoClient('localhost',27017)

def tick_print(symbol, start, end):
    db = conn['Ctp_Tick']
    coll = db[symbol]
    rs = coll.find({'datetime': {'$gte': parse(start), '$lt': parse(end)}}).sort('datetime', -1)
    rs = list(rs)
    df = pd.DataFrame(rs)
    print 'tick count:', len(df)
    if not len(df):
        return
    fields = ['datetime', 'symbol', 'date', 'time', 'volume', 'upperLimit', 'highPrice', 'lastPrice', 'lastVolume',
              'lowPrice', 'lowerLimit', 'openInterest', 'openPrice', 'preClosePrice']
    fields += ['askPrice1', 'askVolume1', 'bidPrice1', 'bidVolume1']
    x = df['datetime'].values
    y = df['lastPrice'].values
    y2 = df['volume'].values

    df.to_csv('{}-{}-{}.csv'.format(symbol, start, end))

    fig, ax = plt.subplots(figsize=(20, 6))
    fig.set()
    # ax.bar( x,y,label='ag1809-')
    ax.plot(x, y, 'go-', label=symbol)

    plt.grid(linewidth=0.5)
    plt.legend()


# 绘制行情k线图 nmin - (1m,3m,5m,15m,30m,1h)
def nmin_print(symbol, nmin, start, end):
    db = conn['Ctp_Bar_{}'.format(nmin)]
    coll = db[symbol]
    rs = coll.find({'datetime': {'$gte': parse(start), '$lt': parse(end)}}).sort('datetime', 1)
    rs = list(rs)
    df = pd.DataFrame(rs)
    print 'bar count:', len(df)
    if not len(df):
        return
    fields = ['datetime', 'symbol', 'date', 'time', 'volume', 'open', 'close', 'high', 'low', 'openInterest']
    x = df['datetime'].values
    y = df['close'].values

    print nmin

    fig, ax = plt.subplots(figsize=(20, 6))
    fig.set()
    ax.set_title('kline-{}- from:{} to:{}'.format(nmin, start, end), loc='left')
    # ax.bar( x,y,label='ag1809-')
    ax.plot(x, y, 'go-', label=symbol)

    plt.grid(linewidth=0.5)
    plt.legend()


# 绘制行情 candle 图 nmin - (1m,3m,5m,15m,30m,1h)
def candle_print(symbol, nmin, start, end):
    db = conn['Ctp_Bar_{}'.format(nmin)]
    coll = db[symbol]
    rs = coll.find({'datetime': {'$gte': parse(start), '$lt': parse(end)}}).sort('datetime', 1)
    rs = list(rs)
    df = pd.DataFrame(rs)
    print 'bar count:', len(df)

    if not len(df):
        return
    fields = ['datetime', 'open', 'close', 'high', 'low', 'volume', 'symbol', 'openInterest', ]
    fields = ['datetime', 'open', 'close', 'high', 'low', 'volume', 'openInterest']
    df = df[fields]
    # data = df.as_matrix()
    data = df.values

    # write into file
    df.to_csv('{}-{}-{}-{}.csv'.format(symbol, nmin, start, end))

    def date_to_num(dates):
        num_time = []
        for date in dates:
            num_date = mpl.dates.date2num(date)
            num_time.append(num_date)
        return num_time

    #     xx = date_to_num(data[:,0])
    data[:, 0] = range(0, len(data))

    fig, ax = plt.subplots(figsize=(15, 8))
    fig.subplots_adjust(bottom=0.5)

    #     ax.set_xticks(range(0,len(data)))

    mpf.candlestick_ochl(ax, data, width=0.6, colorup='r', colordown='g', alpha=1.0)
    plt.grid(True)
    # 设置日期刻度旋转的角度
    plt.xticks(rotation=30)
    plt.title(symbol + ' bar:' + nmin)
    plt.xlabel('Date')
    plt.ylabel('Price')
    # x轴的刻度为日期


#     ax.xaxis_date ()

# 'm1901,RM809,y1809,c1901,AP810,CF901,a1901,hc1810,rb1810'

def tick_print_batch(symbols, start, end):
    for symbol in symbols:
        tick_print(symbol, start, end)


def nmin_print_batch(symbols, scale, start, end):
    for symbol in symbols:
        candle_print(symbol, scale, start, end)


symbols = 'm1901,RM809,y1809,c1901,AP810,CF901,a1901,hc1810,rb1810'.split(',')
symbols = ['m1901']
# tick_print_batch(symbols,'2018-8-13 8:0','2018-8-13 11:32')
scales = ['1m', '3m', '5m', '15m', '30m', '60m']
for scale in scales:
    nmin_print_batch(symbols, scale, '2018-8-13 8:0', '2018-8-13 15:32')
