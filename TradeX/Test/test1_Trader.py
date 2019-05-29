#!/usr/bin/env python
# -*- coding: gb2312 -*-

import msvcrt
import sys
import TradeX2


print "\t1、初始化...\n"
TradeX2.OpenTdx(14, "6.40", 12, 0)

print "\t2、登录交易服务器...\n"


from config import *

try:
    client = TradeX2.Logon(nQsid, sHost, nPort, sVersion, nBranchID, nAccountType, sClientAccount, sBrokerAccount, sPassword, sTxPassword)
except TradeX2.error, e:
    print "error: " + e.message
    TradeX2.CloseTdx()
    msvcrt.getch()
    sys.exit(-1)

print "\n\t成功登录\n"

# print "\n\t按任意键继续...\n"
# msvcrt.getch()

#
#
#
print "\t3、查询资金...\n"

nCategory = 0

status, content = client.QueryData(nCategory)
if status < 0:
    print "error: " + content
else:
    print content

print "\n\t按任意键继续...\n"
msvcrt.getch()

#
#
#
print "\t4、查询股份...\n"

nCategory = 1

status, content = client.QueryData(nCategory)
if status < 0:
    print "error: " + content
else:
    print content

print "\n\t按任意键继续...\n"
msvcrt.getch()

#
#
#
print "\t5、查询可交易股票数量...\n"

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

print "\n\t按任意键继续...\n"
msvcrt.getch()

#
#
#
# print "\t6、一键新股申购...\n"
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
# print "\t7、新股申购明细...\n"
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
# print "\n\t按任意键继续...\n"
# msvcrt.getch()
#
# #
# #
# #
# print "\t8、委托...\n"
#
# status, content = client.SendOrder(0, 4, "p001001001005793", "601988", 0, 100)
# if status < 0:
#     print "error: " + content
# else:
# 	print content
#
# print "\n\t按任意键继续...\n"
# msvcrt.getch()
#
# #
# #
# #
# print "\t9、批量委托...\n"
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
# print "\n\t按任意键继续...\n"
# msvcrt.getch()

#
#
#
print "\t10、查询五档行情...\n"

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

print "\n\t按任意键继续...\n"
msvcrt.getch()

#
#
#
print "\t11、查询资金、持仓...\n"

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

print "\n\t按任意键继续...\n"
msvcrt.getch()

#
#
#
print "\t12、关闭服务器连接...\n"

del client
TradeX2.CloseTdx()

#
#
#
print "\t按任意键退出...\n"

msvcrt.getch()

