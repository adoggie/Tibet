#coding:utf-8

import pymongo
from mantis.fundamental.application.app import instance
from mantis.fundamental.utils.useful import singleton
from mantis.trade.types import TimeDuration,ProductClass
from mantis.trade.errors import ErrorDefs
from vnpy.trader.vtObject import VtTickData,VtBarData
import requests
from mantis.trade import command
from mantis.trade.message import  *


# @singleton
class DataResServiceProxy(object):
    """
    数据资源访问服务
    查询历史行情数据(Tick/Bar)
    """
    def __init__(self,handler,http):
        """

        :param handler:  handler.ProductHandler
        :param http:
        """
        self.http = http
        self.handler = handler

    def queryBars(self,symbol,scale,limit=0,product_class=ProductClass.Future):
        """
        查询k线历史数据
        :param symbol: 合约代码
        :param scale: 时间刻度  1m,5m,15m,30m,1h,1d
        :param limit: 最大记录数 0 为无限制
        :param product_class:  产品类型，默认：期货
        :return:
            result,error
        """
        scale = scale.lower()
        if scale not in TimeDuration.SCALES.keys():
            return ()
        dbname = 'Ctp_Bar_{}'
        conn = instance.datasourceManager.get('mongodb').conn
        if product_class == ProductClass.Stock:
            dbname = 'Stock_Bar_{}'

        dbname = dbname.format(scale)
        coll = conn[dbname][symbol]
        rows = coll.find().sort('datetime', pymongo.DESCENDING).limit(limit)
        bars = []
        for row in rows:
            bar = VtBarData()
            bar.__dict__ = row
            bars.append(bar)
        return bars

    def queryTicks(self,symbol,limit=0,product_class=ProductClass.Future):
        dbname = 'Ctp_Tick'
        conn = instance.datasourceManager.get('mongodb').conn
        if product_class == ProductClass.Stock:
            dbname = 'Stock_Tick'
        coll = conn[dbname][symbol]
        projections =[] #定义返回的字段，默认全返回
        rows = coll.find().sort('datetime',pymongo.DESCENDING).limit(limit)
        ticks = []
        for row in rows:
            tick = VtTickData()
            tick.__dict__ = row
            ticks.append(tick)
        return ticks



@singleton
class PAServiceProxy(object):
    """
    分析服务器访问代理对象
    用于更加复杂的数据处理和分析人物
    通常采用http接口访问，以便负载均衡

    目前在无接口提供功能
    """
    def __init__(self):
        pass


class TradeAdapterProxy(object):
    """对应资金账户"""
    def __init__(self,http):
        """
        :param http: 服务web访问地址前缀
        http://192.168.1.1:8800/v1/message/
        """
        self.http = http

    def request(self,dataCLS,data,error_data=None):
        """
        所有的http请求都默认加上本地服务的策略编号 : strategy_id

        :param dataCLS:
        :param data:
        :param error_data:
        :return:
        """
        main =  instance.serviceManager.get('main')
        strategy_id = main.strategy_id

        msg = Message(dataCLS.NAME,data=data.__dict__,head={'strategy_id':strategy_id}) # todo. 添加本策略标识2018.7.5
        try:
            print ">> ",msg.marshall()
            resp = requests.post(self.http, data=msg.marshall(), timeout= main.cfgs.get('http_request_timeout',0))
            result = dataCLS.Result().assign(resp.json())
            # 传入对象为 CallReturn().json()
            # { status:0,errcode,errmsg,result:{} ]

        except:
            traceback.print_exc()
            return error_data
        return result.value

    def getOrder(self,order_id):
        """查询委托"""
        data = command.GetOrder()
        data.order_id = order_id
        result = self.request(command.GetOrder,data)
        return result

    def getAllWorkingOrders(self):
        """查询所有活动委托（返回列表）"""
        data = command.GetAllWorkingOrders()
        result = self.request(command.GetAllWorkingOrders, data,[])
        return result

    def getAllTrades(self):
        """获取所有成交"""
        data = command.GetAllTrades()
        result = self.request(command.GetAllTrades, data, [])
        return result

    # ----------------------------------------------------------------------
    def getAllPositions(self):
        """获取所有持仓"""
        data = command.GetAllPositions()
        result = self.request(command.GetAllPositions, data, [])
        return result

    # ----------------------------------------------------------------------
    def getAllAccounts(self):
        """获取所有资金"""
        data = command.GetAllAccounts()
        result = self.request(command.GetAllAccounts, data, [])
        return result

    def getCurrentAccount(self):
        accounts = self.getAllAccounts()
        if accounts:
            return accounts[0]
        return None

    # ----------------------------------------------------------------------
    def getPositionDetail(self, vtSymbol):
        return None

    def getAllPositionDetails(self):
        """查询所有本地持仓缓存细节"""
        return []

    def sendOrder(self,order_req,strategy_id):
        """

        :param order_req: VtOrderReq
        :param strategy_id:
        :return:
        """
        data = command.SendOrder()
        data.__dict__ = order_req.__dict__
        orderIds = self.request(command.SendOrder,data,[])
        return orderIds

    def cancelOrder(self,order_id):
        data = command.CancelOrder()
        data.order_id = order_id
        result = self.request(command.CancelOrder,data,False)
        return result

    def cancelAllOrders(self):
        data = command.CancelAllOrders()

        result = self.request(command.CancelAllOrders,data,False)
        return result
