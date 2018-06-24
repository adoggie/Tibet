# coding:utf-8

import os,os.path
import inspect
import yaml
import json
from mantis.trade.types import TimeDuration,BarData,TickData,ProductClass
from mantis.fundamental.application.app import instance
from mantis.trade.strategy import StrategyTask
from context import Context
from proxy import DataResServiceProxy,TradeServiceProxy,PAServiceProxy
from symbol import SymbolTable
from handler import FutureHandler,StockHandler
from mantis.trade.constants import *

from mantis.trade import utils

from mantis.trade.types import ServiceType
from mantis.trade.message import *

class StrategyObject(object):
    def __init__(self):
        self.symbolTable = SymbolTable()

class StrategyController(object):
    def __init__(self,service):
        self.service = service
        self.table = SymbolTable()
        self.ctx = Context()
        self.ctx.controller = self

        # self.tick_symbols = []      #已订阅合约编码

        # self.bar_symbols = {
        #     TimeDuration.MINUTE_1:[], # 1分钟的合约列表
        #     TimeDuration.MINUTE_5:[],
        #     TimeDuration.MINUTE_15:[],
        #     TimeDuration.MINUTE_30:[],
        #     TimeDuration.HOUR_1: [],
        #     TimeDuration.DAY:[]
        # }
        # self.bar_symbols = []
        # self.chans =set()

        self.task = StrategyTask()
        # self.defaultAccount = ''        # 策略中设置默认的资金账户名称，避免每次调用交易时传递账户信息

        self.futureHandler  = FutureHandler(self)
        self.stockHandler   = StockHandler(self)


    def setTimer(self,action=None,timeout=1,user=None):
        if not action:
            action = self.onTimer
        task = self.service.registerTimedTask(action,user=user,timeout=timeout)
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
        self.task = task
        self.ctx.logger = instance.getLogger()

        self.ctx.configs = self.task.strategy.configs
        self.ctx.quotas  = self.task.quotas
        self.ctx.future  = self.futureHandler
        self.ctx.stock   = self.stockHandler

        self.initQuotas()
        self.futureHandler.open()
        self.stockHandler.open()

        self.table.loadModule('strategies.'+module_name+'.main')
        ctx = self.table.get('ctx')
        if ctx.isDefined():
            setattr(ctx.module,ctx.name,self.ctx) # injected controller into strategy-module dynamically

        self.table.invoke('init',self.ctx)

    def initQuotas(self):
        """装配连接交易适配器的命令通道
        """
        for quota in self.task.quotas.values():
            if quota.product == ProductClass.Future:
                self.futureHandler.addAccount(quota)
            if quota.product == ProductClass.Stock:
                self.stockHandler.addAccount(quota)
            # 启动账号交易适配器
            self.startTradeAdapter(quota.account,quota.product)

    def startTradeAdapter(self,account,product):
        # 1. 检测交易适配器是否已启动
        # service_id = TradeAdapterServiceIdFormat.format(product=product,account=account)
        # values = self.service.table.getServiceConfigValues(service_id,ServiceType.TradeAdapter)
        # alive = utils.is_service_alive(values.get('live_time',0))

        # 2. 未启动则请求adapter launcher 加载 adapter
        # if not alive:
        #     msg = Request(name = SystemCommand.StartTradeAdapter)
        #     msg.data =

        # 3. 启动定时器，要求tradeadapter保持运行

        msg = Request(name=SystemCommand.StartTradeAdapter)
        msg.data = dict( product = product,account = account)
        self.sendChannelMessage(CommandChannelTradeAdapterLauncherREAD,msg.marshall())


    def sendChannelMessage(self,channel_name,message,broker_name='redis',channel_type='pubsub'):
        """向指定的通道发送消息
            :param channel_type: pubsub or queue
        """
        broker = instance.messageBrokerManager.get(broker_name)
        chan = broker.createChannel(channel_name,type_=channel_type)
        chan.open()
        chan.publish_or_produce(message)
        return chan

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

    def setDefaultAccount(self,name):
        """设置缺省的资金账户"""
        self.defaultAccount = name
    #=================================================

if __name__ == '__main__':
    StrategyController(None).loadStrategy('strategy_example')
