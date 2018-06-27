#coding:utf-8

from mantis.fundamental.application.app import instance
from mantis.fundamental.utils.useful import singleton
from mantis.trade.types import TimeDuration,ProductClass
from mantis.trade.errors import ErrorDefs
import grequests
from mantis.trade import command
from mantis.trade.message import  *


@singleton
class DataResServiceProxy(object):
    """
    数据资源访问服务
    查询历史行情数据(Tick/Bar)
    """
    def __init__(self):
        pass

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

    def getOrder(self,order_id):
        """查询委托"""
        data = command.GetOrder()
        data.order_id = order_id
        msg = Message(command.GetOrder.NAME,data=data.__dict__)
        try:
            resp = grequests.post(self.http,data = msg.marshall())
            result = command.GetOrder.Result()
            result.assign(resp.json)
            return result.order
        except:
            traceback.print_exc()
        return None

    def getAllWorkingOrders(self):
        """查询所有活动委托（返回列表）"""
        pass

    def getAllTrades(self):
        """获取所有成交"""
        return self.tradeDict.values()

    # ----------------------------------------------------------------------
    def getAllPositions(self):
        """获取所有持仓"""
        return self.positionDict.values()

    # ----------------------------------------------------------------------
    def getAllAccounts(self):
        """获取所有资金"""
        # return self.accountDict.values()
        pass
    # ----------------------------------------------------------------------
    def getPositionDetail(self, vtSymbol):
        pass

    def getAllPositionDetails(self):
        """查询所有本地持仓缓存细节"""
        return self.detailDict.values()

    def sendOrder(self,order_req,strategy_id):
        pass