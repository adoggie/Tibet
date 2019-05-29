#!/usr/bin/env python
# -*- coding: gb2312 -*-

import msvcrt
import sys
import TradeX2


print "\t1����ʼ��...\n"
TradeX2.OpenTdx(14, "6.40", 12, 0)

print "\t2����¼���׷�����...\n"


from config import *

try:
    client = TradeX2.Logon(nQsid, sHost, nPort, sVersion, nBranchID, nAccountType, sClientAccount, sBrokerAccount, sPassword, sTxPassword)
except TradeX2.error, e:
    print "error: " + e.message
    TradeX2.CloseTdx()
    msvcrt.getch()
    sys.exit(-1)

print "\n\t�ɹ���¼\n"

# print "\n\t�����������...\n"
# msvcrt.getch()

#
#
#
print "\t3����ѯ�ʽ�...\n"

nCategory = 0

status, content = client.QueryData(nCategory)
if status < 0:
    print "error: " + content
else:
    print content

print "\n\t�����������...\n"
msvcrt.getch()

#
#
#
print "\t4����ѯ�ɷ�...\n"

nCategory = 1

status, content = client.QueryData(nCategory)
if status < 0:
    print "error: " + content
else:
    print content

print "\n\t�����������...\n"
msvcrt.getch()

#
#
#
print "\t5����ѯ�ɽ��׹�Ʊ����...\n"

nCategory = 0
nPriceType = 0
sAccount = ""
sStockCode = "000002"
fPrice = 3.11

status, content = client.GetTradableQuantity(nCategory, nPriceType, sAccount, sStockCode, fPrice)
if status < 0:
    print "error: " + content
else:
    print content

print "\n\t�����������...\n"
msvcrt.getch()

#
#
#
# print "\t6��һ���¹��깺...\n"
#
# status = client.QuickIPO()
# if status < 0:
#     print "error: " + str(status)
# else:
# 	print "ok: " + str(status)
#
# #
# #
# #
# print "\t7���¹��깺��ϸ...\n"
#
# status, content = client.QuickIPODetail()
# if status < 0:
#     print "error: " + content
# elif status == 0:
# 	print content
# else:
# 	for elem in content:
# 		errinfo, result = elem
# 		if errinfo != "":
# 			print errinfo
# 		else:
# 			print result
#
# print "\n\t�����������...\n"
# msvcrt.getch()
#
# #
# #
# #
# print "\t8��ί��...\n"
#
# status, content = client.SendOrder(0, 4, "p001001001005793", "601988", 0, 100)
# if status < 0:
#     print "error: " + content
# else:
# 	print content
#
# print "\n\t�����������...\n"
# msvcrt.getch()
#
# #
# #
# #
# print "\t9������ί��...\n"
#
# status, content = client.SendOrders(((0, 0, "p001001001005793", "601988", 3.11, 100), (0, 0, "p001001001005793", "601988", 3.11, 200)))
# if status < 0:
# 	print content
# else:
# 	for elem in content:
# 		errinfo, result = elem
# 		if errinfo != "":
# 			print errinfo
# 		else:
# 			print result
#
# print "\n\t�����������...\n"
# msvcrt.getch()

#
#
#
print "\t10����ѯ�嵵����...\n"

# status, content = client.GetQuotes(('000001', '600600'))
status, content = client.GetQuotes(('000001',))
if status < 0:
    print content
else:
    for elem in content:
        errinfo, result = elem
        if errinfo != "":
            print errinfo
        else:
            print result

print "\n\t�����������...\n"
msvcrt.getch()

#
#
#
print "\t11����ѯ�ʽ𡢳ֲ�...\n"

Category = (0, 1, 3)

status, content = client.QueryDatas(Category)
if status < 0:
    print content
else:
    for elem in content:
        errinfo, result = elem
        if errinfo != "":
            print errinfo
        else:
            print result

print "\n\t�����������...\n"
msvcrt.getch()

#
#
#
print "\t12���رշ���������...\n"

del client
TradeX2.CloseTdx()

#
#
#
print "\t��������˳�...\n"

msvcrt.getch()

