# coding: utf-8

import json

from vnpy.event import EventEngine2
from vnpy.trader.vtEvent import EVENT_LOG, EVENT_ERROR,EVENT_TICK
from vnpy.trader.vtEngine import MainEngine, LogEngine
from vnpy.trader.gateway import ctpGateway
from vnpy.trader.vtObject import VtSubscribeReq, VtLogData, VtBarData, VtTickData
from vnpy.trader.vtEvent import *
from vnpy.trader.vtGateway import *

from mantis.fundamental.application.app import instance
from mantis.fundamental.utils.useful import hash_object
from mantis.fundamental.service import ServiceBase


class ContractService(ServiceBase):
    """数据引擎"""

    # ----------------------------------------------------------------------
    def __init__(self,name):
        super(ServiceBase, self).__init__(name)
        self.ee = None
        self.mainEngine = None
        self.logger = instance.getLogger()


    def init(self, cfgs):
        self.cfgs = cfgs

    def start(self, block):
        # 创建日志引擎
        #
        le = self.logger
        # le = LogEngine()
        # le.setLogLevel(le.LEVEL_INFO)
        # le.addConsoleHandler()
        le.info(u'启动行情记录运行子进程')

        self.ee = EventEngine2()
        le.info(u'事件引擎创建成功')

        self.mainEngine = MainEngine(self.ee,self)
        self.mainEngine.addGateway(ctpGateway)

        le.info(u'主引擎创建成功')

        self.registerEvent()

        le.info(u'注册日志事件监听')

        cfgs = self.cfgs.get('gateway', {})
        self.mainEngine.connect(cfgs.get('name'), cfgs)

        le.info(u'连接CTP接口')

    def stop(self):
        self.mainEngine.exit()

    def join(self):
        pass
    # ----------------------------------------------------------------------
    def registerEvent(self):
        """注册事件监听"""
        self.ee.register(EVENT_CONTRACT, self.processContractEvent)
        # self.ee.register(EVENT_LOG, self.processLogEvent)
        # self.ee.register(EVENT_ERROR, self.processErrorEvent)

    # ----------------------------------------------------------------------
    def processContractEvent(self, event):
        """处理合约事件
           连接交易系统之后,会通过此接口接收到CTP所有当前合约
        """
        contract = event.dict_['data']

        redis = instance.datasourceManager.get('redis').conn
        CTA_CONTRACTS_KEY = self.cfgs.get('CTA_CONTRACTS_KEY')
        dictData = {contract.symbol: json.dumps(hash_object(contract))}
        redis.hmset(CTA_CONTRACTS_KEY, dictData)

        # 写入mongodb的db0数据库的coll0记录表

        if contract.last:
            instance.stop()
