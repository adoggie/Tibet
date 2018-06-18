# coding: utf-8

from mantis.fundamental.utils.useful import singleton
from mantis.fundamental.application.app import instance
from mantis.trade.bar import BarGenerator
from mantis.trade.types import TimeScale

class SymbolBarCollection(object):
    """一个合约具有多种时间k线条

    """
    def __init__(self,symbol):
        self.symbol = symbol
        self.bgmin = BarGenerator('1m',self.onBar) #
        self.bglist = {}

    def init(self,barNames):
        for name in barNames:
            if name != '1m':
                bg = BarGenerator(name,None,xmin=TimeScale.SCALES.get(name),onXminBar=self.onXminBar)
                self.bglist[name] = bg

    def onBar(self,bar):
        """由1分钟累积到多分钟Bar"""
        for bg in self.bglist:
            bg.updateBar(bar)  # 达到 n 分钟将促发 onXminBar
        scale = '1m'
        main = instance.serviceManager.get('main')
        main.onXminBar(scale,bar) #

    def onTick(self,tick):
        """

        :param tick: (VtTickData)
        :return:
        """

        self.bgmin.updateTick(tick)

    def onXminBar(self,bar,bg):
        """一个时间周期的k线数据
        """
        scale = bg.name
        # 将 minbar 发布到pubsub上去
        main = instance.serviceManager.get('main')
        main.onXminBar(scale,bar)


@singleton
class SymbolBarManager(object):
    def __init__(self):
        self.symbol_bars = {}  #
        self.bars = []

    def init(self,bars):
        """

        :param bars:  generate_bars: '1m,5m,15m,30m,1h'
        :return:
        """
        bars = bars.strip().lower().split(',')
        if sum([ TimeScale.SCALES.keys().count(b) for b in bars]) == 0:
            # bars 项存在非法命名的情况
            return False
        self.bars = bars

    def onTick(self,symbol,tick):
        """

        :param symbol:
        :param tick:  (VtTickData)
        :return:
        """

        bc = self.symbol_bars.get(symbol)
        if not bc:
            bc = SymbolBarCollection(symbol)
            bc.init(self.bars)
        bc.onTick(tick)

