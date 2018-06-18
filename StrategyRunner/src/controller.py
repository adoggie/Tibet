# coding:utf-8

import os,os.path
import inspect
import yaml
from collections import OrderedDict
from mantis.fundamental.utils.importutils import import_module
from mantis.trade.types import TimeDuration,BarData,TickData,ProductClass
from mantis.fundamental.application.app import instance
from mantis.trade.strategy import StrategyTask
from context import Context
from proxy import DataResServiceProxy,TradeServiceProxy,PAServiceProxy

class SymbolMatched(object):
    def __init__(self,matches,must=0,optional=0):
        """

        :param matches:
        :param must: 必填参数个数
        :param optional: 可选参数个数
        """
        self.matches = matches  # 匹配的符号名称列表
        # self.var = None         # 匹配上的模块属性
        self.name = None        # 符号名称
        # self.varnames = []      # hold arguments for function
        self.module = None
        # self.defined = False

    @property
    def var(self):
        return getattr(self.module,self.name)

    def isDefined(self):
        return self.name

    def isfunction(self):

        return inspect.isfunction( self.var )

    def function_arguments(self):
        funcs = {}

        for name,func in  inspect.getmembers(self.var,inspect.isfunction):
            funcs[name] = func.__code__.co_varnames

    def arguments(self):
        """返回函数对象的参数名称"""

        if inspect.isfunction(self.var):
            return self.var.__code__.co_varnames
        return []

    def matched(self,name):
        """检查name是否在匹配模式列表"""
        if self.matches.count(name.lower()) == 0:
            return False
        return True

    def __call__(self, *args, **kwargs):
        self.var(*args,**kwargs)
    # def match(self,mo):

class SymbolTable(object):
    """ 策略模块定义符号表,可以是变量或函数
    """
    def __init__(self):
        self.symbols = OrderedDict()

        self.initTable()

    def initTable(self):
        """ 支持多种匹配的符号名称定义
            支持策略模块中的多符号名称映射，且不区分大小写，当Controller触发相应事件时在symbolTable定位回调对象
        """
        self.symbols['ctx']     = SymbolMatched(['ctx','context'],0,0)  #
        self.symbols['init']    = SymbolMatched(['oninit','init','on_init'],0,1)  #
        self.symbols['start']   = SymbolMatched(['onstart','start','on_start'],0,1)  #
        self.symbols['stop']    = SymbolMatched(['onstop','stop','on_stop'],0,1)  #
        self.symbols['ontick']  = SymbolMatched(['ontick','on_tick'],1,1)  #
        self.symbols['onbar']   = SymbolMatched(['onbar','on_bar'],1,1)  #
        self.symbols['onorder'] = SymbolMatched(['onorder','on_order'],1,1)  #
        self.symbols['ontrade'] = SymbolMatched(['ontrade','on_trade'],1,1)  #


    def loadModule(self,module_name):
        module = import_module(module_name)
        members = OrderedDict()
        symbols = dir(module)
        for name in symbols:
            if name.startswith('__'):
                continue
            members[name] = getattr(module,name) # 读取所有模块内的符号对象

        for name,member in members.items():
            for _,sm in self.symbols.items():   #符号名匹配
               if sm.matched(name):
                   sm.name = name
                   sm.module = module

        #
        print self.symbols
        # for s in self.symbols.values():
        #     print s.name,s.var

    def get(self,name):
        return self.symbols.get(name)

    def invoke(self,name,*args):
        func = self.get(name)
        if func.isDefined():
            args = args[:len(func.arguments())]
            func(*args)

            # if len(func.arguments()):
            #     func(*args)
            # else:
            #     func()


class StrategyObject(object):
    def __init__(self):
        self.symbolTable = SymbolTable()

class StrategyController(object):
    def __init__(self,service):
        self.service = service
        self.table = SymbolTable()
        self.ctx = Context()
        self.ctx.controller = self
        self.tick_symbols = []      #已订阅合约编码
        self.bar_symbols = {
            TimeDuration.MINUTE_1:[], # 1分钟的合约列表
            TimeDuration.MINUTE_5:[],
            TimeDuration.MINUTE_15:[],
            TimeDuration.MINUTE_30:[],
            TimeDuration.HOUR_1: [],
            TimeDuration.DAY:[]
        }
        self.bar_symbols = []
        self.chans =set()


    @property
    def dataResServer(self):
        pass

    @property
    def paServer(self):
        pass

    @property
    def tradeServer(self):
        pass

    def setTimer(self,action=None,timeout=1):
        if not action:
            action = self.onTimer
        task = self.service.registerTimedTask(action,timeout=timeout)
        return task

    def killTimer(self,timer):
        self.service.unregisterTimedTask(timer)

    def loadStrategy(self,module_name):
        """加载策略模块文件，
        默认路径： <./strategies/>
        """
        path = os.path.join(instance.getHomePath(), 'src/strategies', module_name)
        filename = os.path.join(path, 'config.yaml')

        cfgs = yaml.load(open(filename).read())
        if not cfgs:
            print 'Error: config.yaml not be found.'
            return

        task = StrategyTask()
        task.loads(cfgs)
        self.ctx.task = task

        self.table.loadModule('strategies.'+module_name+'.main')
        ctx = self.table.get('ctx')
        if ctx.isDefined():
            setattr(ctx.module,ctx.name,self.ctx) # injected controller into strategy-module dynamically
        self.table.invoke('init',self.ctx)

    def open(self):
        self.table.invoke('start',self.ctx)

    def close(self):
        self.table.invoke('stop',self.ctx)
        self.ctx.controller = None


    def onTick(self,tick):
        self.table.invoke('ontick',tick,self.ctx)

    def onBar(self,bar):
        self.table.invoke('onbar',bar,self.ctx)

    def onOrder(self,order):
        self.table.invoke('onorder',order,self.ctx)

    def onTrade(self,trade):
        self.table.invoke('ontrade',trade,self.ctx)

    def onTimer(self,timer_id):
        self.table.invoke('ontimer',timer_id,self.ctx)

    def onStopOrder(self,order):
        self.table.invoke('onstoporder',order,self.ctx)

    def subTicks(self,symbol,gateway='ctp'):
        """
        订阅行情Tick数据
        从redis的pubsub中订阅指定的产品
        """
        key = self.service.getConfig().get('tick_sub_key')
        key = key.format(gateway = gateway, symbol = symbol)
        broker = instance.messageBrokerManager.get('redis')
        chan = broker.createPubsubChannel(key, self._handler_tick)
        self.chans.add(chan)
        chan.open()
        chan.props['symbol'] = symbol
        chan.props['gateway'] = gateway

    def _handler_tick(self,message,ctx):
        chan = ctx.get('channel')
        data = TickData()
        data.data = message
        data.symbol = chan.props.get('symbol')
        data.gateway = chan.props.get('gateway')
        self.onTick(data)


    def subBars(self,symbol,scale,gateway='ctp'):
        """
        订阅指定类型的k线数据
        """
        scale = scale.lower()
        gateway = gateway.lower()
        if scale not in TimeDuration.SCALES.keys():
            return False
        # subkey = '{gateway}_bar_{symbol}_{scale}'.format(
        #         gateway=self.ctx.task.trade_account.gateway.lower(),
        #     symbol = symbol,scale = scale
        # )
        subkey = self.service.getConfig().get('bar_sub_key')
        subkey = subkey.format(
            gateway=gateway,
            symbol=symbol, scale=scale
        )

        broker = instance.messageBrokerManager.get('redis')
        chan = broker.createPubsubChannel(subkey,self._handler_bar)
        self.chans.add(chan)
        chan.open()
        chan.props['symbol'] = symbol
        chan.props['scale'] = scale
        chan.props['gateway'] = gateway

    def _handler_bar(self,message,ctx):
        chan = ctx.get('channel')
        data = BarData()
        data.data = message
        data.symbol = chan.props.get('symbol')
        data.scale = chan.props.get('scale')
        data.gateway = chan.props.get('gateway')
        self.onBar(data)


    #=================================================
    def sell(self, price, volume, stop=False):
        """卖平"""
        return self.sendOrder(CTAORDER_SELL, price, volume, stop)

        # ----------------------------------------------------------------------

    def short(self, price, volume, stop=False):
        """卖开"""
        return self.sendOrder(CTAORDER_SHORT, price, volume, stop)

        # ----------------------------------------------------------------------

    def cover(self, price, volume, stop=False):
        """买平"""
        return self.sendOrder(CTAORDER_COVER, price, volume, stop)

    # ----------------------------------------------------------------------
    def sendOrder(self, orderType, price, volume, stop=False):
        """发送委托"""
        if self.trading:
            # 如果stop为True，则意味着发本地停止单
            if stop:
                vtOrderIDList = self.ctaEngine.sendStopOrder(self.vtSymbol, orderType, price, volume, self)
            else:
                vtOrderIDList = self.ctaEngine.sendOrder(self.vtSymbol, orderType, price, volume, self)
            return vtOrderIDList
        else:
            # 交易停止时发单返回空字符串
            return []

    # ----------------------------------------------------------------------
    def cancelOrder(self, vtOrderID):
        """撤单"""
        # 如果发单号为空字符串，则不进行后续操作
        if not vtOrderID:
            return

        if STOPORDERPREFIX in vtOrderID:
            self.ctaEngine.cancelStopOrder(vtOrderID)
        else:
            self.ctaEngine.cancelOrder(vtOrderID)

    # ----------------------------------------------------------------------
    def cancelAll(self):
        """全部撤单"""
        self.ctaEngine.cancelAll(self.name)

    def loadTick(self, symbol, days=1,limit =0 , product_class=ProductClass.Future):
        """读取tick数据
        向 DataResService 发起 http 查询请求
        :param symbol: 合约代码
        :param days:  距今天数
        :param limit: 最大的bar数量 , 0: 未限制
        """
        return DataResServiceProxy().queryTicks(symbol,days,limit,product_class)

    # ----------------------------------------------------------------------
    def loadBar(self, symbol,scale,days=1,limit=0,product_class=ProductClass.Future):
        """读取bar数据
        :param symbol: 合约代码
        :param scale : bar时间宽度 1m,5m,15m,..
        :param days:  距今天数
        :param limit: 最大的bar数量 , 0: 未限制
        """
        return DataResServiceProxy().queryBars(symbol,days,limit,product_class)


if __name__ == '__main__':
    StrategyController(None).loadStrategy('strategy_example')
