#coding:utf-8

import time
import os
from threading import Thread
from mantis.fundamental.application.app import instance
from mantis.fundamental.service import ServiceBase
from mantis.fundamental.basetype import ValueEntry
from .types import ServiceType,TradeAccountInfo
from .table import ServiceRuntimeTable

class TimedTask(object):
    SECOND = 1
    MINUTE = SECOND * 60

    def __init__(self,action,user_data =None,timeout= SECOND):
        self.action = action
        self.timeout = timeout
        self.start_time = 0
        self.user = user_data
        self.times = 0


    def start(self):
        self.start_time = time.time()

    def stop(self):
        self.start_time = 0

    def execute(self):
        if self.start_time and self.start_time + self.timeout < time.time():
            self.start_time = time.time()
            if self.action:
                self.action(self)
                self.times+=1

class ServiceRunStatus(object):
    STOPPED = 'stopped'
    RUNNING = 'running'
    PAUSED  = 'paused'




class ServiceCommonProperty(object):
    ServiceId   = ValueEntry('service_id',u'系统编号')
    ServiceType = ValueEntry('service_type',u'服务类型')
    Host        = ValueEntry('host',u'主机地址')
    LiveTime    = ValueEntry('live_time',u'最近一次活跃时间 ')
    StartTime   = ValueEntry('start_time',u'运行开始时间')
    Status      = ValueEntry('status',u'运行状态 STOPPED/RUNNING/PAUSED')
    LauncherId  = ValueEntry('launcher_id',u'装载器编号')
    PID         = ValueEntry('pid',u'进程号')
    AccessUrl   = ValueEntry('access_url',u'管理接口')
    LogUrl      = ValueEntry('log_url',u'日志输出接口 ')

class ServicePropertyFrontLauncher(object):
    TradeAdapterIDs     = ValueEntry('trade_adapter_ids',u'资金交易适配程序编号')
    MarketAdapterIDs    = ValueEntry('market_adapter_ids',u'行情适配服务编号')

# class ProductClass(object):
#     Future = ValueEntry('future',u'期货')
#     Stock   = ValueEntry('stock',u'股票')

class ServicePropertyFrontService(object):
    """这里指 market , trade 前端接入服务"""
    ProductClass    = ValueEntry('product_class',u'产品类型')
    Exchange        = ValueEntry('exchange',u'交易市场')
    Gateway         = ValueEntry('gateway',u'')
    Broker          = ValueEntry('broker',u'期货公司')
    User            = ValueEntry('user',u'开户名称')
    Password        = ValueEntry('password',u'账户密码')
    MarketServerAddress    = ValueEntry('market_server_address',u'行情服务器')
    TradeServerAddress  = ValueEntry('trade_server_address',u'交易服务器')
    AuthCode = ValueEntry('auth_code',u'登陆用户认证码')
    UserProductInfo = ValueEntry('user_product_info',u'用户产品信息')

class ServicePropertyMarketAdapter(object):
    SubscribeContracts  = ValueEntry('subscribe_contracts',u'准备订阅的合约编号')

class TradeFrontServiceTraits(TradeAccountInfo):
    def __init__(self):
        TradeAccountInfo.__init__(self)


    def syncDownServiceConfig(self):
        self.product_class  = self.cfgs_remote.get(ServicePropertyFrontService.ProductClass.v)
        self.gateway  = self.cfgs_remote.get(ServicePropertyFrontService.Gateway.v)
        self.exchange        = self.cfgs_remote.get(ServicePropertyFrontService.Exchange.v)
        self.broker         = self.cfgs_remote.get(ServicePropertyFrontService.Broker.v)
        self.user           = self.cfgs_remote.get(ServicePropertyFrontService.User.v)
        self.password       = self.cfgs_remote.get(ServicePropertyFrontService.Password.v)
        self.market_server_addr = self.cfgs_remote.get(ServicePropertyFrontService.MarketServerAddress.v)
        self.trade_server_addr  = self.cfgs_remote.get(ServicePropertyFrontService.TradeServerAddress.v)
        self.auth_code  = self.cfgs_remote.get(ServicePropertyFrontService.AuthCode.v)
        self.user_product_info  = self.cfgs_remote.get(ServicePropertyFrontService.UserProductInfo.v)

    def convertToVnpyGatewayConfig(self):
        cfgs = dict( userID = self.user,
                     password = self.password,
                     brokerID = self.broker,
                     tdAddress = self.trade_server_addr,
                     mdAddress = self.market_server_addr
                     )
        if self.auth_code:
            cfgs['authCode'] = self.auth_code

        if self.user_product_info:
            cfgs['userProductInfo'] = self.user_product_info
        return cfgs

class TradeService(ServiceBase):
    def __init__(self,name):
        super(TradeService,self).__init__(name)
        self._thread = None
        self.isclosed = False
        self.timed_taskes =set()
        self.service_id = None
        self.service_type = ServiceType.UnDefined
        self.table = None

        self.cfgs_remote = {}       # 存储在 redis 中的服务配置参数
        self.access_url = ''
        self.log_url = ''
        self.fanout_switchers ={}

        self.logger = None

    def getServiceId(self):
        return self.service_id

    def getServiceType(self):
        return self.service_type.value

    def init(self,cfgs):
        self.cfgs = cfgs
        self.table = ServiceRuntimeTable() #.instance()
        conn = instance.datasourceManager.get('redis').conn
        ServiceRuntimeTable().setRedis(conn)

        host = 'localhost'
        pid = os.getpid()

        dict_ = {
            str(ServiceCommonProperty.LiveTime): time.time(),
            str(ServiceCommonProperty.ServiceId): self.getServiceId(),
            str(ServiceCommonProperty.ServiceType): self.getServiceType(),
            str(ServiceCommonProperty.Host): host,
            str(ServiceCommonProperty.StartTime): time.time(),
            str(ServiceCommonProperty.Status): ServiceRunStatus.RUNNING,
            str(ServiceCommonProperty.PID): pid
        }
        self.table.updateServiceConfigValues(self.getServiceId(), self.getServiceType(),**dict_)

        self.syncDownServiceConfig()

    def initFanoutSwitchers(self,cfgs):
        from .fanout import FanoutSwitcher
        for cf in cfgs:
            fs = FanoutSwitcher(self,cf)
            self.fanout_switchers[fs.name] = fs

    def dataFanout(self,switcher,data,**names):
        fs = self.fanout_switchers.get(switcher)
        if fs:
            fs.fanout(data,**names)

    def syncDownServiceConfig(self):
        """下载通用的配置信息"""
        cfgs =  self.table.getServiceConfigValues(self.getServiceId(),self.getServiceType())
        self.access_url = cfgs.get(ServiceCommonProperty.AccessUrl,'')
        self.log_url = cfgs.get(ServiceCommonProperty.LogUrl,'')
        self.cfgs_remote = cfgs

    def start(self):

        self.registerTimedTask(self.updateLiveStatus,self)
        self._thread = Thread(target=self._run)
        self._thread.start()

    def stop(self):
        self.isclosed = True

    def join(self):
        if self._thread:
            self._thread.join()


    def registerTimedTask(self,action,user=None,timeout=TimedTask.SECOND):
        let = TimedTask(action,user,timeout)
        self.timed_taskes.add(let)
        let.start()
        return let

    def unregisterTimedTask(self,let):
        let.stop()
        self.timed_taskes.remove(let) # don't worry about the lock protection

    def _run(self):
        self.isclosed = False

        while not self.isclosed:
            for task in self.timed_taskes:
                task.execute()
            time.sleep(0.1)

    def updateLiveStatus(self,task):
        """
        注册服务运行状态
        :return:
        """
        # print 'times:',task.times,'user:',task.user
        dict_=  {
            ServiceCommonProperty.LiveTime.v: time.time(),
        }
        self.table.updateServiceConfigValues(self.getServiceId(),self.getServiceType(),
                                             **dict_
                                             )