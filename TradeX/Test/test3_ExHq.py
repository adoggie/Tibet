#!/usr/bin/env python
# -*- coding: gb2312 -*-

import msvcrt
import sys
import TradeX2


print "\t*******************************************************************"
print "\t*                        TradeX2.dll v1.4.0                       *"
print "\t*                                                                 *"
print "\t*  TradeX2.dll ��Ʊ���򻯽��׽ӿ�ȫ�·�����                       *"
print "\t*                                                                 *"
print "\t*  �汾������                                                     *"
print "\t*  1��֧����ͨ�˻���������ȯ�����˻�ҵ�񣬰����µ�����������ѯ��  *"
print "\t*  ������ȯ��ҵ��                                               *"
print "\t*  2�������������µ��Ͷ��˻�ͬʱ�µ���ÿ�������µ��ɴ����ٵ���    *"
print "\t*  3��֧�ֹ�Ʊ�嵵��Level 2ʮ��ʵʱ�����Լ��ڻ�����չ���飬��     *"
print "\t*  ��ͬʱ����������ȡ���飻                                       *"
print "\t*  4��ֱ�����׷����������������������ת����ȫ���ȶ���ʵ�������У�*"
print "\t*  5��ȫ��C++��C#��Python��Delphi��Java�������Ե����Խӿڣ�       *"
print "\t*  6����������trade.dll�����׽����̩���������������⡣           *"
print "\t*                                                                 *"
print "\t*  ����QQȺ��318139137  QQ��3048747297                            *"
print "\t*  ������ҳ��https://tradexdll.com/                               *"
print "\t*  http://pan.baidu.com/s/1jIjYq1K                                *"
print "\t*                                                                 *"
print "\t*******************************************************************"

print "\n\t�����������...\n"
msvcrt.getch()

#
#
#
sHost = "61.152.107.141"
nPort = 7727

print "\t1���������������", sHost, "... "

try:
	clientExHq = TradeX2.TdxExHq_Connect(sHost, nPort)
except TradeX2.TdxExHq_error, e:
	print "error: " + e.message
	msvcrt.getch()
	sys.exit(-1)

print "\n\t���ӳɹ�!\n"

print "\n\t�����������...\n"
msvcrt.getch()

#
#
#
print "\t2����ȡ�г�����...\n"

errinfo, result = clientExHq.GetMarkets()
if errinfo != "":
	print errinfo
else:
	print result

print "\n\t�����������...\n"
msvcrt.getch()

#
#
#
print "\t3����ѯ�г�����Ʒ����...\n"

errinfo, count = clientExHq.GetInstrumentCount()
if errinfo != "":
	print errinfo
else:
	print count

print "\n\t�����������...\n"
msvcrt.getch()

#
#
#
print "\t4����ѯ��Ʒ��Ϣ...\n"

nStart = 0

errinfo, count, result = clientExHq.GetInstrumentInfo(nStart)  
if errinfo != "":
	print errinfo
else:
	print count
	print result

print "\n\t�����������...\n"
msvcrt.getch()

#
#
#
print "\t5����ѯ��Ʒ����...\n"

nMarket = 47
StockCode = "IF1706"

errinfo, result = clientExHq.GetInstrumentQuote(nMarket, StockCode)
if errinfo != "":
	print errinfo
else:
	print result

print "\n\t�����������...\n"
msvcrt.getch()

#
#
#
print "\t6����ѯ��ƷK��...\n"

nCategory = 9
nMarket = 47
StockCode = "IF1706"
nStart = 0
nCount = 100

errinfo, count, result = clientExHq.GetInstrumentBars(nCategory, nMarket, StockCode, nStart, nCount)
if errinfo != "":
	print errinfo
else:
	print count
	print result

print "\n\t�����������...\n"
msvcrt.getch()

#
#
#
print "\t7����ѯ��ʱ...\n"

nMarket = 47
StockCode = "IF1706"

errinfo, result = clientExHq.GetMinuteTimeData(nMarket, StockCode)
if errinfo != "":
	print errinfo
else:
	print result

print "\n\t�����������...\n"
msvcrt.getch()

#
#
#
print "\t8����ѯ��ʱ��ʷ...\n"

nMarket = 47
StockCode = "IF1706"
nDate = 20170222

errinfo, result = clientExHq.GetHistoryMinuteTimeData(nMarket, StockCode, nDate)
if errinfo != "":
	print errinfo
else:
	print result

print "\n\t�����������...\n"
msvcrt.getch()

#
#
#
print "\t9����ѯ�ֱʳɽ�...\n"

nMarket = 47
StockCode = "IF1706"
nStart = 0
nCount = 10

errinfo, count, result = clientExHq.GetTransactionData(nMarket, StockCode, nStart, nCount)
if errinfo != "":
	print errinfo
else:
	print count
	print result

print "\n\t�����������...\n"
msvcrt.getch()

#
#
#
print "\t10����ѯ��ʷ�ֱʳɽ�...\n"

nMarket = 47
StockCode = "IF1706"
nStart = 0
nCount = 10
nDate = 20170222

errinfo, count, result = clientExHq.GetHistoryTransactionData(nMarket, StockCode, nDate, nStart, nCount)
if errinfo != "":
	print errinfo
else:
	print count
	print result

#
#
#
print "\n\t��������˳�...\n"
msvcrt.getch()

del clientExHq

print "\t------------------------------------------------------------\n"
print "\t����\n"



