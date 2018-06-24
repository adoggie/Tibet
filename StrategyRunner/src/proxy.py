#coding:utf-8

from mantis.fundamental.application.app import instance
from mantis.fundamental.utils.useful import singleton
from mantis.trade.types import TimeDuration,ProductClass
from mantis.trade.errors import ErrorDefs


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


class TradeAdapterProxy(object):
    """对应资金账户"""
    def __init__(self):
        pass


@singleton
class TradeServiceProxy(object):
    """资金交易管理服务"""
    def __init__(self):
        self.adapters = {} #
        """
        product_class:
          gateway_name:
            user
              password
              mdAddress
        
        examples:
        future.ctp
            u001:
        
        """

    def openAccount(self):
        """"""

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
