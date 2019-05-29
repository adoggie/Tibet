#!/usr/bin/env python
# -*- coding: gb2312 -*-

import msvcrt
import sys
import TradeX2


print "\t*******************************************************************"
print "\t*                        TradeX2.dll v1.4.0                       *"
print "\t*                                                                 *"
print "\t*  TradeX2.dll 股票程序化交易接口全新发布！                       *"
print "\t*                                                                 *"
print "\t*  版本描述：                                                     *"
print "\t*  1）支持普通账户和融资融券信用账户业务，包括下单、撤单、查询，  *"
print "\t*  融资融券等业务；                                               *"
print "\t*  2）批量多连接下单和多账户同时下单，每秒批量下单可达数百单；    *"
print "\t*  3）支持股票五档、Level 2十档实时行情以及期货等扩展行情，允     *"
print "\t*  许同时批量多连接取行情；                                       *"
print "\t*  4）直连交易服务器和行情服务器，无中转，安全、稳定，实盘运行中；*"
print "\t*  5）全新C++，C#，Python，Delphi，Java，易语言等语言接口；       *"
print "\t*  6）完美兼容trade.dll，彻底解决华泰服务器的连接问题。           *"
print "\t*                                                                 *"
print "\t*  技术QQ群：318139137  QQ：3048747297                            *"
print "\t*  技术首页：https://tradexdll.com/                               *"
print "\t*  http://pan.baidu.com/s/1jIjYq1K                                *"
print "\t*                                                                 *"
print "\t*******************************************************************"

print "\n\t按任意键继续...\n"
msvcrt.getch()

#
#
#

# 行情服务器主机
sHost = "183.3.223.36"
nPort = 7709
L2User = "togogo"
#L2Password = "new@trial"
L2Password = "Zaq1xsw2"

print "\t连接行情服务器", sHost, "... "

try:
	clientL2Hq = TradeX2.TdxL2Hq_Connect(sHost, nPort, L2User, L2Password)
except TradeX2.TdxL2Hq_error, e:
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

errinfo, count = clientL2Hq.GetSecurityCount(nMarket)
if errinfo != "":
	print errinfo
else:
	print "\t深市股票数量：", count, "\n"

#
#
#
print "\t3、查询沪市股票数量...\n"

nMarket =1    # 0 - 深圳  1 - 上海

errinfo, count = clientL2Hq.GetSecurityCount(nMarket)
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

errinfo, count, result = clientL2Hq.GetSecurityList(nMarket, nStart)
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

errinfo, count, result = clientL2Hq.GetSecurityBars(nCategory, nMarket, sStockCode, nStart, nCount)
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
print "\t10、查询指数K线\n"

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

print "\n\t按任意键继续...\n"
msvcrt.getch()

#
#
#
print "\t11、查询分时行情...\n"

nMarket = 0
sStockCode = "000001"

errinfo, result = clientL2Hq.GetMinuteTimeData(nMarket, sStockCode)
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

errinfo, result = clientL2Hq.GetHistoryMinuteTimeData(nMarket, sStockCode, nDate)
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

errinfo, count, result = clientL2Hq.GetTransactionData(nMarket, sStockCode, nStart, nCount)
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

errinfo, count, result = clientL2Hq.GetHistoryTransactionData(nMarket, sStockCode, nStart, nCount, nDate)
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

errinfo, result = clientL2Hq.GetCompanyInfoCategory(nMarket, sStockCode)
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

errinfo, result = clientL2Hq.GetCompanyInfoContent(nMarket, sStockCode, '000001.txt', 221077, 39547)
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

errinfo, result = clientL2Hq.GetXDXRInfo(nMarket, sStockCode)
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

errinfo, result = clientL2Hq.GetFinanceInfo(nMarket, sStockCode)
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
print "\t20、查询十档股票行情...\n"

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

print "\n\t按任意键继续...\n"
msvcrt.getch()

#
#
#
print "\t21、查询逐笔委托行情...\n"

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
	
print "\n\t按任意键继续...\n"
msvcrt.getch()

#
#
#
print "\t22、查询逐笔成交行情...\n"

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
	
print "\n\t按任意键继续...\n"
msvcrt.getch()

#
#
#
print "\t23、查询买卖队列数据...\n"

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
print "\n\t按任意键退出...\n"
msvcrt.getch()

del clientL2Hq

print "\t------------------------------------------------------------\n"
print "\t结束\n"


