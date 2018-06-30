#coding:utf-8

from mantis.fundamental.application.app import instance
from mantis.fundamental.utils.useful import singleton
from mantis.trade.types import TimeDuration,ProductClass
from mantis.trade.errors import ErrorDefs
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

    def queryBars(self,symbol,scale,days,limit=0,product_class=ProductClass.Future):
        """
        查询k线历史数据
        :param symbol: 合约代码
        :param scale: 时间刻度  1m,5m,15m,30m,1h,1d
        :param start: 开始时间
        :param end:  结束时间
        :param limit: 最大记录数 0 为无限制
        :param product_class:  产品类型，默认：期货
        :return:
            result,error
        """
        scale = scale.lower()
        if scale not in TimeDuration.SCALES.keys():
            return ()

    def queryTicks(self,symbol,days,limit=0,product_class=ProductClass.Future):
        pass




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

        :param dataCLS:
        :param data:
        :param error_data:
        :return:
        """

        msg = Message(dataCLS.NAME,data=data.__dict__)
        try:
            resp = requests.post(self.http, data=msg.marshall(), timeout=2)
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