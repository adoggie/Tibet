#coding:utf-8

from datetime import datetime as DateTime,timedelta as TimeDelta,time as Time
import time
import pandas as pd
import numpy as np
from dateutil.parser import parse
from dateutil.rrule import *
import pymongo
import  mantis.trade.kline as kline

# conn = pymongo.MongoClient('localhost',27017)
conn = pymongo.MongoClient('mongodb',27017)

kline.mongodb_conn = conn

def test_make_min():
    """
    生成指定合约每分钟的k线数据
    """
    f = open('test.txt','w')
    # 读取某一日所有交易分钟k线时间点
    mins =  kline.get_day_trade_minute_line('M',parse('2018-9-5'))
    ss = '\n'.join(map(str,mins))
    f.write(ss)
    f.close()

    for min in mins:
        print 'Make Kline:',str(min)
        kline.make_min_bar('m1901',min,drop=True)

def test_make_nmin():
    f = open('test2.txt','w')
    # 计算一日N分钟间隔的交易k线时间点
    mins =  kline.get_day_trade_nminute_line('M',3,parse('2018-8-1'))
    ss = '\n'.join(map(str,mins))
    f.write(ss)
    f.close()
    #
    for min in mins:
        print 'Make Kline:',str(min)
        kline.make_min_bar('AP901',min,'3m',drop=True)

def test_repeat_min_bar():
    """模拟交易时间连续进行最近分钟k线计算"""
    f = open('test3.txt','w')
    start = parse('2018-8-6 9:10')
    dt = start
    while dt < parse('2018-8-7 3:20'):
        bar = kline.make_lastest_min_bar('AP901',dt)
        dt += TimeDelta(seconds=1)
        # print dt
        if bar:
            text =  'Repeat Time:'+ str(dt) + ' Bar:' + str(bar.__dict__)
            f.write('{}\n'.format(text))
        # time.sleep(.2)
    f.close()


def test_repeat_nmin_bar(scale):
    """模拟交易时间连续进行最近N分钟k线计算"""
    f = open('test-{}.txt'.format(scale), 'w')
    start = parse('2018-8-6 9:10')
    dt = start
    end = parse('2018-8-7 3:10')
    while dt < end:
        # bar = kline.make_lastest_min_bar('AP901', dt)
        bar = None
        bar = kline.make_latest_nmin_bar('AP901', scale,dt)
        dt += TimeDelta(seconds=1)
        if bar:
            text = 'Repeat Time:' + str(dt) + ' Bar:' + str(bar.__dict__)
            f.write('{}\n'.format(text))
            f.flush()
        # print str(dt)
        #time.sleep(.2)
    f.close()

# test_repeat_min_bar()
test_repeat_nmin_bar('3m')
test_repeat_nmin_bar('5m')
test_repeat_nmin_bar('15m')
test_repeat_nmin_bar('30m')
test_repeat_nmin_bar('1h')
# test_make_nmin()
# test_make_min()