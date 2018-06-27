# coding:utf-8


import os,sys

# from mantis.fundamental.application.use_gevent import USE_GEVENT
# if USE_GEVENT:
#     from gevent.queue import Queue
# else:
#     from Queue import Queue

# from threading import Thread
# from datetime import datetime, time
# from vnpy.trader.vtEvent import EVENT_LOG, EVENT_ERROR,EVENT_TICK
# from vnpy.trader.vtObject import VtSubscribeReq, VtLogData, VtBarData, VtTickData

from mantis.fundamental.application.app import instance
from mantis.trade.strategy import StrategyRunMode
from mantis.trade.service import TradeService,TradeFrontServiceTraits,ServiceType,ServiceCommonProperty
from controller import StrategyController
from optparse import OptionParser
from command import create,list,upload,pull,remove,run_local_name,run_server_strategy_id
from mantis.trade.constants import *

class StrategyRunner(TradeService):
    def __init__(self,name):
        TradeService.__init__(self,name)

        # self.active = False  # 工作状态
        # self.queue = Queue()  # 队列
        # self.thread = Thread(target=self.threadDataFanout)  # 线程
        self.logger = instance.getLogger()
        # self.symbols = {} # 已经订阅的合约
        self.controller = None
        self.runmode = StrategyRunMode.Null


    def init(self, cfgs,**kwargs):
        """
        策略运行接收运行参数 run  --name --sid
        将 name ,sid作为系统运行id的附加后缀

        :param cfgs:
        :param kwargs:
        :return:
        """
        self.parseOptions()

        if self.runmode == StrategyRunMode.Null:
            instance.abort()
            return
        super(StrategyRunner,self).init(cfgs)

    def parseOptions(self):
        command = ''
        if len(sys.argv) < 2:
            print 'Error: Command Must Be (CREATE,LIST,PULL,UPLOAD,REMOVE AND RUN ).'
            raise RuntimeError()
        command = sys.argv[1].lower()
        if command not in ('create','list','pull','upload','remove','run'):
            return False

        parser = OptionParser()
        parser.add_option("--user",dest='user')
        parser.add_option("--password",dest='password')
        # parser.add_option("--name",dest='name')
        # parser.add_option("--sid",dest='sid')   # 策略编号
        parser.add_option("--remote",action='store_false',dest='isremote')   # 策略编号

        parser.add_option("--launcher_id",dest='launcher') # 加载器编号


        args = sys.argv[2:]
        (options, args) = parser.parse_args(args)
        if len(args)==0:
            print 'Error: strategy name missed.'
            return False

        strategy_name = ''
        if args:
            strategy_name = args[0]

        self.runmode = StrategyRunMode.Null

        if command == 'create': # create s1
            create(strategy_name,DevelopUserStrategyKeyPrefix)

        if command == 'list':
            list(strategy_name,DevelopUserStrategyKeyPrefix)

        if command =='pull':
            pull(strategy_name,DevelopUserStrategyKeyPrefix)

        if command == 'remove':
            remove(strategy_name,DevelopUserStrategyKeyPrefix)

        if command == 'upload':
            upload(strategy_name,DevelopUserStrategyKeyPrefix)

        if command == 'run':
            if not options.isremote: # run local project
                self.runmode = StrategyRunMode.Development
                self.service_id = strategy_name
                self.service_type = ServiceType.StrategyDevRunner
                # run_local_name(strategy_name,DevelopUserStrategyKeyPrefix,self)
            else:
                self.service_id = strategy_name
                self.service_type = ServiceType.StrategyRunner
                self.runmode = StrategyRunMode.Product  #
                # run_server_strategy_id(strategy_name,self)

    def syncDownServiceConfig(self):
        TradeService.syncDownServiceConfig(self)

    def setupFanoutAndLogHandler(self):
        from mantis.trade.log import TradeServiceLogHandler
        self.initFanoutSwitchers(self.cfgs.get('fanout'))
        handler = TradeServiceLogHandler(self)
        self.logger.addHandler(handler)

    def start(self,block=True):
        self.controller = StrategyController(self)
        self.setupFanoutAndLogHandler()
        if self.runmode == StrategyRunMode.Product:
            run_server_strategy_id(self.service_id,self)
        if self.runmode == StrategyRunMode.Development:
            run_local_name(self.service_id,DevelopUserStrategyKeyPrefix,self)

        # 创建日志引擎
        TradeService.start(self)


    def stop(self):
        TradeService.stop(self)
        # if self.active:
        #     self.active = False

    def initCommandChannels(self):
        TradeService.initCommandChannels(self)
        channel = self.createServiceCommandChannel(CommandChannelTradeAdapterLauncherSub,open=True)
        self.registerCommandChannel('trade_adapter_launcher',channel)

    def handle_channel_read(self,data,ctx):
        pass