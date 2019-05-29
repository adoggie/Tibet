#!/usr/bin/env python
#coding:utf-8
## -*- coding: gb2312 -*-

import msvcrt
import sys
import TradeX2
import datetime
from dateutil.parser import parse
from mantis.sg.fisher import model as model

def init_mongodb(host='127.0.0.1',port=27017,date = None):
    """
    date : str 默认为当日
    """
    from pymongo import MongoClient




    mg_conn = MongoClient(host, port)
    return mg_conn




date = None
conn = init_mongodb(host='192.168.1.252', date=date)


def get_code_hq(code):
    """查询当日指定股票行情，返回 昨收，今收价格"""
    from mantis.sg.fisher.stutils import get_trade_database_name

    date = datetime.datetime.now()
    dbname = 'TDX_%04d-%02d-%02d_Ticks'%(date.year, date.month, date.day)
    coll = conn[dbname][code]
    rs = coll.find().sort('time',-1).limit(1)
    r = list(rs)[0]
    last = r['last']
    yd_close = r['yd_close']

    dbname = get_trade_database_name()
    coll = conn[dbname]['CodeSettings']
    rs = coll.find({'code':code}).limit(1)[0]
    name = rs['name']
    return last,yd_close,name


print "\t1、初始化...\n"
TradeX2.OpenTdx(14, "6.40", 12, 0)

print "\t2、登录交易服务器...\n"


# from config import *

cfgs = dict(id='aijian', name=u'爱建证券1',
     qsid=35, host="139.224.94.170", port=7708,
     version="6.57", branch_id=101, account_type=9, account_no="190120000330",
     trade_account_no="190120000330", password="171025",
     tx_password="171025",
     client_account="190120000330",
     broker_account="190120000330",
     quote_host="61.49.50.190", quote_port=7709,
     broker_name='AIJIAN'
     )

nQsid = cfgs['qsid']
sHost = cfgs['host']
nPort = cfgs['port']
sVersion = cfgs['version']
nBranchID = cfgs['branch_id']
nAccountType = cfgs['account_type']
sClientAccount = cfgs['client_account']
sBrokerAccount = cfgs['broker_account']
sPassword = cfgs['password']
sTxPassword = cfgs['tx_password']

try:
    client = TradeX2.Logon(nQsid, sHost, nPort, sVersion, nBranchID, nAccountType, sClientAccount, sBrokerAccount, sPassword, sTxPassword)
except TradeX2.error, e:
    print "error: " + e.message.decode('gbk')
    TradeX2.CloseTdx()
    msvcrt.getch()
    sys.exit(-1)

print "\n\t成功登录\n"

# print "\n\t按任意键继续...\n"
# msvcrt.getch()

#
#
#

buy_total = []
sell_total = []

print "\t3、交易记录查询...\n"

nCategory = 3

status, content = client.QueryData(nCategory)
if status < 0:
    print "error: " + content
else:
    print content.decode('gbk')

lines = content.decode('gbk').split("\n")
lines = lines[1:]

lines = map(lambda _: _.strip(), lines)
lines = filter(lambda _: _, lines)
for line in lines:
    fs = line.strip().split('\t')
    print len(fs)
    for i, _ in enumerate(fs):
        print i, _.encode('utf-8')
    direction = 'buy'
    if int(fs[3]) == 1:
        direction = 'sell'

    price = float(fs[6])
    volumn = float(fs[7])
    amount = float(fs[8])
    code = fs[1]
    time = fs[0]

    total = sell_total
    if direction == 'buy':
        total = buy_total

    ps = get_code_hq(code)
    last,yd_close,name = ps
    total.append(dict(time=time,code=code,name=name,price=price,volumn=volumn,amount=amount ,last = last ,yd_close = yd_close ))

stat_file = './trade_state.csv'
fp = open(stat_file,'w')

fmt = u',时间,证券代码,名称,成交价,成交量,成交金额,最新价格,昨日收盘价, 价格盈亏浮动率\n'
fp.write(fmt.encode('gbk'))

for _ in buy_total:
    time = _['time']
    code = "'"+ _['code']
    price = _['price']
    volumn = _['volumn']
    amount = _['amount']
    last = _['last']
    yd_close = _['yd_close']
    name = _['name']

    zf = (price - yd_close)/yd_close
    fmt = u'买入,{},{},{},{},{},{},{},{},{}\n'.format(time,code,name,price,volumn,amount,last,yd_close,zf)
    fp.write(fmt.encode('gbk'))

for _ in sell_total:
    time = _['time']
    code = "'" +  _['code']
    price = _['price']
    volumn = _['volumn']
    amount = _['amount']
    last = _['last']
    yd_close = _['yd_close']
    name = _['name']

    zf = (price - yd_close)/yd_close
    fmt = u'卖出,{},{},{},{},{},{},{},{},{}\n'.format(time,code,name,price,volumn,amount,last,yd_close,zf)
    fp.write(fmt.encode('gbk'))

fp.close()
print buy_total
print sell_total
#
#
print "\t4、查询股份...\n"

nCategory = 1

status, content = client.QueryData(nCategory)
if status < 0:
    print "error: " + content
else:
    print content.decode('gbk')

print "\t12、关闭服务器连接...\n"

del client
TradeX2.CloseTdx()
