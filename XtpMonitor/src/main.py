# coding:utf-8

from mantis.fundamental.application.use_gevent import USE_GEVENT
if USE_GEVENT:
    from gevent.queue import Queue
else:
    from Queue import Queue

import json
import datetime,time
from threading import Thread
from datetime import datetime, time
from collections import OrderedDict

from mantis.fundamental.application.app import instance
from mantis.fundamental.utils.timeutils import datetime_to_timestamp
from mantis.trade.service import TradeService,ServiceType,ServiceCommonProperty
from mantis.trade.constants import *
from xtpmon_wrap import *

class XtpMonitorService(TradeService):
    def __init__(self,name):
        TradeService.__init__(self,name)

        self.active = False  # 工作状态
        self.queue = Queue()  # 队列
        # self.thread = Thread(target=self.threadDataFanout)  # 线程
        self.ee = None
        self.mainEngine = None
        self.logger = instance.getLogger()
        self.symbols = {} # 已经订阅的合约
        self.contracts = OrderedDict()
        self.ticks_counter = 0
        self.ticks_samples = []
        self.tick_filters =[]

    def init(self, cfgs,**kwargs):
        self.service_id = cfgs.get('id')
        self.service_type = ServiceType.XtpMonitor
        super(XtpMonitorService,self).init(cfgs)
        self.init_xtp_monitor()

    def setupFanoutAndLogHandler(self):
        from mantis.trade.log import TradeServiceLogHandler
        self.initFanoutSwitchers(self.cfgs.get('fanout'))

        handler = TradeServiceLogHandler(self)
        self.logger.addHandler(handler)

    def onMonitorClientLogin(self,username,password,mac_addr,ip):
        print 'Xtp Monitor Client Login ..'
        print username,password,mac_addr,ip
        print 'Passed ..'
        return 0

    def onStart(self):
        print 'Remote Command: Start ..'
        return 0

    def onStop(self):
        print 'Remote Command: Stop ..'
        return 0

    def init_xtp_monitor(self,block=True):
        # 注意： 必须保留 StartFunc(onStart) 的函数对象为全局，避免被GC回收导致回调异常
        # self.start_func , self.stop_func , self.monitor_client_func 必须被保持，避免GC回收导致回调异常

        self.start_func = StartFunc(self.onStart)
        self.stop_func = StopFunc(self.onStop)
        self.monitor_client_func = MonitorClientLoginFunc(self.onMonitorClientLogin)
        RegisterStartFunc(self.start_func)
        RegisterStopFunc(self.stop_func)
        RegisterMonitorClientLoginFunc(self.monitor_client_func)

        server = self.cfgs.get('server')
        ip = server.get('host')
        port = server.get('port')
        username = server.get('username')
        password = server.get('password')
        ret = ConnectToMonitor(ip, port, username, True)
        print 'Connect XtpHost :', ret
        if ret != 0:
            instance.abort()
            print 'System Exit..'

    def start(self,block=False):
        self.setupFanoutAndLogHandler()
        # 创建日志引擎
        super(XtpMonitorService,self).start()
        # self.active = True
        # self.thread.start()
        # self.registerTimedTask(self.sendMessage)

    def sendLogDetail(self,msg):
        level = 1
        topic = "debug message"
        text = msg.plainText
        index = 1
        SendMsg(level,topic,text,index)

    def stop(self):
        super(XtpMonitorService,self).stop()

    def join(self):
        # self.thread.join()
        TradeService.join(self)
        pass

