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
sHost = "61.152.107.141"
nPort = 7727

print "\t1、连接行情服务器", sHost, "... "

try:
	clientExHq = TradeX2.TdxExHq_Connect(sHost, nPort)
except TradeX2.TdxExHq_error, e:
	print "error: " + e.message
	msvcrt.getch()
	sys.exit(-1)

print "\n\t连接成功!\n"

print "\n\t按任意键继续...\n"
msvcrt.getch()

#
#
#
print "\t2、获取市场代码...\n"

errinfo, result = clientExHq.GetMarkets()
if errinfo != "":
	print errinfo
else:
	print result

print "\n\t按任意键继续...\n"
msvcrt.getch()

#
#
#
print "\t3、查询市场中商品数量...\n"

errinfo, count = clientExHq.GetInstrumentCount()
if errinfo != "":
	print errinfo
else:
	print count

print "\n\t按任意键继续...\n"
msvcrt.getch()

#
#
#
print "\t4、查询商品信息...\n"

nStart = 0

errinfo, count, result = clientExHq.GetInstrumentInfo(nStart)  
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
print "\t5、查询商品行情...\n"

nMarket = 47
StockCode = "IF1706"

errinfo, result = clientExHq.GetInstrumentQuote(nMarket, StockCode)
if errinfo != "":
	print errinfo
else:
	print result

print "\n\t按任意键继续...\n"
msvcrt.getch()

#
#
#
print "\t6、查询商品K线...\n"

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

print "\n\t按任意键继续...\n"
msvcrt.getch()

#
#
#
print "\t7、查询分时...\n"

nMarket = 47
StockCode = "IF1706"

errinfo, result = clientExHq.GetMinuteTimeData(nMarket, StockCode)
if errinfo != "":
	print errinfo
else:
	print result

print "\n\t按任意键继续...\n"
msvcrt.getch()

#
#
#
print "\t8、查询分时历史...\n"

nMarket = 47
StockCode = "IF1706"
nDate = 20170222

errinfo, result = clientExHq.GetHistoryMinuteTimeData(nMarket, StockCode, nDate)
if errinfo != "":
	print errinfo
else:
	print result

print "\n\t按任意键继续...\n"
msvcrt.getch()

#
#
#
print "\t9、查询分笔成交...\n"

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

print "\n\t按任意键继续...\n"
msvcrt.getch()

#
#
#
print "\t10、查询历史分笔成交...\n"

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
print "\n\t按任意键退出...\n"
msvcrt.getch()

del clientExHq

print "\t------------------------------------------------------------\n"
print "\t结束\n"



