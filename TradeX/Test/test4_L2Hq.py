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

# �������������
sHost = "183.3.223.36"
nPort = 7709
L2User = "togogo"
#L2Password = "new@trial"
L2Password = "Zaq1xsw2"

print "\t�������������", sHost, "... "

try:
	clientL2Hq = TradeX2.TdxL2Hq_Connect(sHost, nPort, L2User, L2Password)
except TradeX2.TdxL2Hq_error, e:
	print "error: " + e.message
	msvcrt.getch()
	sys.exit(-1)

print "\n\t���ӳɹ�!\n"

print "\n\t�����������...\n"
msvcrt.getch()

#
#
#
print "\t2����ѯ���й�Ʊ����...\n"

nMarket = 0    # 0 - ����  1 - �Ϻ�

errinfo, count = clientL2Hq.GetSecurityCount(nMarket)
if errinfo != "":
	print errinfo
else:
	print "\t���й�Ʊ������", count, "\n"

#
#
#
print "\t3����ѯ���й�Ʊ����...\n"

nMarket =1    # 0 - ����  1 - �Ϻ�

errinfo, count = clientL2Hq.GetSecurityCount(nMarket)
if errinfo != "":
	print errinfo
else:
	print "\t���й�Ʊ������", count, "\n"

print "\n\t�����������...\n"
msvcrt.getch()

#
#
#
print "\t4����ѯ��Ʊ�б�...\n"

nMarket = 0
nStart = 0

errinfo, count, result = clientL2Hq.GetSecurityList(nMarket, nStart)
if errinfo != "":
	print errinfo
else:
	print count
	for line in result.split("\n"):
		print line

print "\n\t�����������...\n"
msvcrt.getch()

#
#
#

# K ������
# 0 -   5 ����K ��
# 1 -   15 ����K ��
# 2 -   30 ����K ��
# 3 -   1 СʱK ��
# 4 -   ��K ��
# 5 -   ��K ��
# 6 -   ��K ��
# 7 -   1 ����
# 8 -   1 ����K ��
# 9 -   ��K ��
# 10 -  ��K ��
# 11 -  ��K ��

print "\t5����ѯ��ƱK��\n"

nCategory = 9
nMarket = 0
sStockCode = "000001"
nStart = 0
nCount = 10

errinfo, count, result = clientL2Hq.GetSecurityBars(nCategory, nMarket, sStockCode, nStart, nCount)
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
print "\t10����ѯָ��K��\n"

nCategory = 9
nMarket = 1
sStockCode = "000001"
nStart = 0
nCount = 10

errinfo, count, result = clientL2Hq.GetIndexBars(nCategory, nMarket, sStockCode, nStart, nCount)
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
print "\t11����ѯ��ʱ����...\n"

nMarket = 0
sStockCode = "000001"

errinfo, result = clientL2Hq.GetMinuteTimeData(nMarket, sStockCode)
if errinfo != "":
	print errinfo
else:
	print result

print "\n\t�����������...\n"
msvcrt.getch()

#
#
#
print "\t12����ѯ��ʷ��ʱ����...\n"

nMarket = 0
sStockCode = "000001"
nDate = 20161209

errinfo, result = clientL2Hq.GetHistoryMinuteTimeData(nMarket, sStockCode, nDate)
if errinfo != "":
	print errinfo
else:
	print result

print "\n\t�����������...\n"
msvcrt.getch()

#
# ��ѯ��ʱ����
#
print "\t13����ѯ��ʱ�ɽ�...\n"

nMarket = 0
sStockCode = "000001"
nStart = 0
nCount = 10

errinfo, count, result = clientL2Hq.GetTransactionData(nMarket, sStockCode, nStart, nCount)
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
print "\t14����ѯ��ʷ��ʱ�ɽ�...\n"

nMarket = 0
sStockCode = "000001"
nStart = 0
nCount = 10
nDate = 20170209

errinfo, count, result = clientL2Hq.GetHistoryTransactionData(nMarket, sStockCode, nStart, nCount, nDate)
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
print "\t15����ѯ��˾��Ϣ...\n"

nMarket = 0
sStockCode = "000001"

errinfo, result = clientL2Hq.GetCompanyInfoCategory(nMarket, sStockCode)
if errinfo != "":
	print errinfo
else:
	print result

print "\n\t�����������...\n"
msvcrt.getch()

#
#
#
print "\t16����ѯ��˾��ϸ��Ϣ...\n"

nMarket = 0
sStockCode = "000001"

errinfo, result = clientL2Hq.GetCompanyInfoContent(nMarket, sStockCode, '000001.txt', 221077, 39547)
if errinfo != "":
	print errinfo
else:
	print result

print "\n\t�����������...\n"
msvcrt.getch()

#
#
#
print "\t17����ѯ��Ȩ��Ϣ����...\n"

errinfo, result = clientL2Hq.GetXDXRInfo(nMarket, sStockCode)
if errinfo != "":
	print errinfo
else:
	print result
	
print "\n\t�����������...\n"
msvcrt.getch()

#
#
#
print "\t18����ѯ��������...\n"

errinfo, result = clientL2Hq.GetFinanceInfo(nMarket, sStockCode)
if errinfo != "":
	print errinfo
else:
	print result
	
print "\n\t�����������...\n"
msvcrt.getch()

#
#
#
print "\t19����ѯ��Ʊ����...\n"

nMarket1 = 0
sStockCode1 = '000001'
nMarket2 = 1
sStockCode2 = '600300'

errinfo, count, result = clientL2Hq.GetSecurityQuotes(((nMarket1, sStockCode1), (nMarket2, sStockCode2)))
if errinfo != "":
	print errinfo
else:
	print count
	for line in result.split("\n"):
		print line

#
#
#
print "\t20����ѯʮ����Ʊ����...\n"

nMarket1 = 0
sStockCode1 = '000001'
nMarket2 = 1
sStockCode2 = '600300'

errinfo, count, result = clientL2Hq.GetSecurityQuotes10(((nMarket1, sStockCode1), (nMarket2, sStockCode2)))
if errinfo != "":
	print errinfo
else:
	print count
	for line in result.split("\n"):
		print line

print "\n\t�����������...\n"
msvcrt.getch()

#
#
#
print "\t21����ѯ���ί������...\n"

nMarket = 0
sStockCode = "000001"
nStart = 0
nCount = 10

errinfo, count, result = clientL2Hq.GetDetailOrderData(nMarket, sStockCode, nStart, nCount)
if errinfo != "":
	print errinfo
else:
	print count
	for line in result.split("\n"):
		print line
	
print "\n\t�����������...\n"
msvcrt.getch()

#
#
#
print "\t22����ѯ��ʳɽ�����...\n"

nMarket = 0
sStockCode = "000001"
nStart = 0
nCount = 10

errinfo, count, result = clientL2Hq.GetDetailTransactionData(nMarket, sStockCode, nStart, nCount)
if errinfo != "":
	print errinfo
else:
	print count
	for line in result.split("\n"):
		print line
	
print "\n\t�����������...\n"
msvcrt.getch()

#
#
#
print "\t23����ѯ������������...\n"

nMarket = 0
sStockCode = "000001"

errinfo, result = clientL2Hq.GetBuySellQueue(nMarket, sStockCode)
if errinfo != "":
	print errinfo
else:
	print result

#
#
#
print "\n\t��������˳�...\n"
msvcrt.getch()

del clientL2Hq

print "\t------------------------------------------------------------\n"
print "\t����\n"


