#!/usr/bin/env python
# -*- coding: gb2312 -*-

import msvcrt
import sys
import TradeX2
from config import *

#
# print "\t*******************************************************************"
# print "\t*                        TradeX2.dll v1.4.0                       *"
# print "\t*                                                                 *"
# print "\t*  TradeX2.dll 股票程序化交易接口全新发布！                       *"
# print "\t*                                                                 *"
# print "\t*  版本描述：                                                     *"
# print "\t*  1）支持普通账户和融资融券信用账户业务，包括下单、撤单、查询，  *"
# print "\t*  融资融券等业务；                                               *"
# print "\t*  2）批量多连接下单和多账户同时下单，每秒批量下单可达数百单；    *"
# print "\t*  3）支持股票五档、Level 2十档实时行情以及期货等扩展行情，允     *"
# print "\t*  许同时批量多连接取行情；                                       *"
# print "\t*  4）直连交易服务器和行情服务器，无中转，安全、稳定，实盘运行中；*"
# print "\t*  5）全新C++，C#，Python，Delphi，Java，易语言等语言接口；       *"
# print "\t*  6）完美兼容trade.dll，彻底解决华泰服务器的连接问题。           *"
# print "\t*                                                                 *"
# print "\t*  技术QQ群：318139137  QQ：3048747297                            *"
# print "\t*  技术首页：https://tradexdll.com/                               *"
# print "\t*  http://pan.baidu.com/s/1jIjYq1K                                *"
# print "\t*                                                                 *"
# print "\t*******************************************************************"
#
#
# #  1 :               招商证券深圳行情    119.147.212.81:7709
# #  2 :             华泰证券(南京电信)    221.231.141.60:7709
# #  3 :             华泰证券(上海电信)    101.227.73.20:7709
# #  4 :           华泰证券(上海电信二)    101.227.77.254:7709
# #  5 :             华泰证券(深圳电信)    14.215.128.18:7709
# #  6 :             华泰证券(武汉电信)    59.173.18.140:7709
# #  7 :             华泰证券(天津联通)    60.28.23.80:7709
# #  8 :             华泰证券(沈阳联通)    218.60.29.136:7709
# #  9 :             华泰证券(南京联通)    122.192.35.44:7709
# # 10 :             华泰证券(南京联通)    122.192.35.44:7709
#
# # 行情服务器主机
sHost = "221.231.141.60"
sHost = "101.227.73.20"
sHost = "101.227.73.130"
sHost = "61.49.50.190"
nPort = 7709
#
# # sHost = "222.173.22.53"
# # nPort = 7700
# sHost = "119.147.171.205"
# nPort = 443
#
#
# print "\n\t按任意键继续...\n"
# msvcrt.getch()

#
#
#
print "\t1、连接行情服务器", sHost, "... "

try:
	clientHq = TradeX2.TdxHq_Connect(sHost, nPort)
except TradeX2.TdxHq_error, e:
	print "error: " + e.message
	msvcrt.getch()
	sys.exit(-1)

print "\n\t连接成功!\n"

print "\n\t按任意键继续...\n"
msvcrt.getch()

#
#
#
print "\t2、查询深市股票数量...\n"

nMarket = 0    # 0 - 深圳  1 - 上海

errinfo, count = clientHq.GetSecurityCount(nMarket)
if errinfo != "":
	print errinfo
else:
	print "\t深市股票数量：", count, "\n"

#
#
#
print "\t3、查询沪市股票数量...\n"

nMarket =1    # 0 - 深圳  1 - 上海

errinfo, count = clientHq.GetSecurityCount(nMarket)
if errinfo != "":
	print errinfo
else:
	print "\t沪市股票数量：", count, "\n"

print "\n\t按任意键继续...\n"
msvcrt.getch()

#
#
#
print "\t4、查询股票列表...\n"

nMarket = 0
nStart = 0

errinfo, count, result = clientHq.GetSecurityList(nMarket, nStart)
if errinfo != "":
	print errinfo
else:
	print count
	for line in result.split("\n"):
		print line

print "\n\t按任意键继续...\n"
msvcrt.getch()

#
#
#

# K 线种类
# 0 -   5 分钟K 线
# 1 -   15 分钟K 线
# 2 -   30 分钟K 线
# 3 -   1 小时K 线
# 4 -   日K 线
# 5 -   周K 线
# 6 -   月K 线
# 7 -   1 分钟
# 8 -   1 分钟K 线
# 9 -   日K 线
# 10 -  季K 线
# 11 -  年K 线

print "\t5、查询股票K线\n"

nCategory = 9
nMarket = 0
sStockCode = "000001"
nStart = 0
nCount = 10

errinfo, count, result = clientHq.GetSecurityBars(nCategory, nMarket, sStockCode, nStart, nCount)
if errinfo != "":
	print errinfo
else:
	print count
	print result

print "\n\t按任意键继续...\n"
msvcrt.getch()

#
#
#
# print "\t10、查询指数K线\n"
#
# nCategory = 9
# nMarket = 1
# sStockCode = "000001"
# nStart = 0
# nCount = 10
#
# errinfo, count, result = clientHq.GetIndexBars(nCategory, nMarket, sStockCode, nStart, nCount)
# if errinfo != "":
# 	print errinfo
# else:
# 	print count
# 	print result
#
# print "\n\t按任意键继续...\n"
# msvcrt.getch()

#
#
#
print "\t11、查询分时行情...\n"

nMarket = 0
sStockCode = "000001"

errinfo, result = clientHq.GetMinuteTimeData(nMarket, sStockCode)
if errinfo != "":
	print errinfo
else:
	print result

print "\n\t按任意键继续...\n"
msvcrt.getch()

#
#
#
print "\t12、查询历史分时行情...\n"

nMarket = 0
sStockCode = "000001"
nDate = 20161209

errinfo, result = clientHq.GetHistoryMinuteTimeData(nMarket, sStockCode, nDate)
if errinfo != "":
	print errinfo
else:
	print result

print "\n\t按任意键继续...\n"
msvcrt.getch()

#
# 查询分时行情
#
print "\t13、查询分时成交...\n"

nMarket = 0
sStockCode = "000001"
nStart = 0
nCount = 10

errinfo, count, result = clientHq.GetTransactionData(nMarket, sStockCode, nStart, nCount)
if errinfo != "":
	print errinfo
else:
	print count
	print result
	
print "\n\t按任意键继续...\n"
msvcrt.getch()

#
#
#
print "\t14、查询历史分时成交...\n"

nMarket = 0
sStockCode = "000001"
nStart = 0
nCount = 10
nDate = 20170209

errinfo, count, result = clientHq.GetHistoryTransactionData(nMarket, sStockCode, nStart, nCount, nDate)
if errinfo != "":
	print errinfo
else:
	print count
	print result

print "\n\t按任意键继续...\n"
msvcrt.getch()

#
#
#
print "\t15、查询公司信息...\n"

nMarket = 0
sStockCode = "000001"

errinfo, result = clientHq.GetCompanyInfoCategory(nMarket, sStockCode)
if errinfo != "":
	print errinfo
else:
	print result

print "\n\t按任意键继续...\n"
msvcrt.getch()

#
#
#
print "\t16、查询公司详细信息...\n"

nMarket = 0
sStockCode = "000001"

errinfo, result = clientHq.GetCompanyInfoContent(nMarket, sStockCode, '000001.txt', 221077, 39547)
if errinfo != "":
	print errinfo
else:
	print result

print "\n\t按任意键继续...\n"
msvcrt.getch()

#
#
#
print "\t17、查询除权除息数据...\n"

errinfo, result = clientHq.GetXDXRInfo(nMarket, sStockCode)
if errinfo != "":
	print errinfo
else:
	print result
	
print "\n\t按任意键继续...\n"
msvcrt.getch()

#
#
#
print "\t18、查询财务数据...\n"

errinfo, result = clientHq.GetFinanceInfo(nMarket, sStockCode)
if errinfo != "":
	print errinfo
else:
	print result
	
print "\n\t按任意键继续...\n"
msvcrt.getch()

#
#
#
print "\t19、查询股票行情...\n"

nMarket1 = 0
sStockCode1 = '000001'
nMarket2 = 1
sStockCode2 = '600300'

errinfo, count, result = clientHq.GetSecurityQuotes(((nMarket1, sStockCode1), (nMarket2, sStockCode2)))
if errinfo != "":
	print errinfo
else:
	print count
	for line in result.split("\n"):
		print line

#
#
#
print "\n\t按任意键退出...\n"
msvcrt.getch()

del clientHq

print "\t------------------------------------------------------------\n"
print "\t结束\n"


