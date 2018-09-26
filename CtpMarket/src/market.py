# coding:utf-8

from mantis.fundamental.application.use_gevent import USE_GEVENT

if USE_GEVENT:
    from gevent.queue import Queue
else:
    from Queue import Queue

import json
import time
from threading import Thread
from collections import OrderedDict
import datetime
import copy
from vnpy.event import EventEngine
from vnpy.trader.vtEvent import EVENT_LOG, EVENT_ERROR, EVENT_TICK, \
    EVENT_CONTRACT, EVENT_DATA
from vnpy.trader.vtEngine import MainEngine
from vnpy.trader.gateway import ctpGateway
from vnpy.trader.vtObject import VtSubscribeReq,\
    VtTickData,VtContractCommissionRateData,VtDepthMarketData
from mantis.fundamental.application.app import instance
from mantis.fundamental.utils.timeutils import datetime_to_timestamp
from mantis.fundamental.utils.useful import singleton
from mantis.trade.service import TradeService, TradeFrontServiceTraits, ServiceType
from mantis.trade.constants import *



class MarketService(TradeService, TradeFrontServiceTraits):
    def __init__(self, name):
        TradeService.__init__(self, name)
        TradeFrontServiceTraits.__init__(self)

        self.active = False  # 工作状态
        self.queue = Queue()  # 队列
        self.thread = Thread(target=self.threadDataFanout)  # 线程
        self.ee = None
        self.mainEngine = None
        self.logger = instance.getLogger()
        self.symbols = {}  # 已经订阅的合约
        self.contracts = OrderedDict()
        self.ticks_counter = 0
        self.ticks_samples = []
        self.tick_filters = []
        self.contract_ticks = {}  # { symbol: tick }
        self.gatewayName = 'CTP'
        self.contract_commissions = OrderedDict() # 合约手续费

    def init(self, cfgs, **kwargs):
        self.service_id = cfgs.get('id')
        self.service_type = ServiceType.MarketAdapter
        super(MarketService, self).init(cfgs)
        self.initFilters()

    def syncDownServiceConfig(self):
        TradeService.syncDownServiceConfig(self)
        TradeFrontServiceTraits.syncDownServiceConfig(self)

        # cfg_gateway = self.cfgs.get('gateway')
        # self.product_class = 'FUTURES'  # self.cfgs_remote.get(ServicePropertyFrontService.ProductClass.v)
        # self.exchange = cfg_gateway.get('name')
        # self.gateway = cfg_gateway.get('name')
        # self.broker = cfg_gateway.get('brokerID')
        # self.user = cfg_gateway.get('userID')
        # self.password = cfg_gateway.get('password')
        # self.market_server_addr = cfg_gateway.get('mdAddress')
        # self.trade_server_addr = cfg_gateway.get('tdAddress')
        # self.auth_code = cfg_gateway.get('authCode')
        # self.user_product_info = cfg_gateway.get('userProductInfo')

    def setupFanoutAndLogHandler(self):
        from mantis.trade.log import TradeServiceLogHandler
        self.initFanoutSwitchers(self.cfgs.get('fanout'))
        handler = TradeServiceLogHandler(self)
        self.logger.addHandler(handler)

    def start(self, block=True):
        self.setupFanoutAndLogHandler()

        # 创建日志引擎
        super(MarketService, self).start()
        self.active = True
        self.thread.start()

        le = self.logger
        # le = LogEngine()
        # le.setLogLevel(le.LEVEL_INFO)
        # le.addConsoleHandler()
        le.info(u'启动行情记录运行子进程')

        self.ee = EventEngine()
        le.info(u'事件引擎创建成功')

        self.mainEngine = MainEngine(self.ee)  # 忽略掉 默认的 DataEngine
        self.mainEngine.addGateway(ctpGateway)
        le.info(u'主引擎创建成功')

        le.info(u'注册日志事件监听')

        self.registerEvent()
        cfgs = self.cfgs.get('gateway',{}) # 本地加载
        # cfgs = self.convertToVnpyGatewayConfig()

        self.subscribeSymbols()

        gateway = self.mainEngine.getGateway('CTP')
        gateway.qryEnabled = False  # disable internel query taskes
        self.mainEngine.connect(ctpGateway.gatewayName, cfgs)

        le.info(u'连接CTP接口')
        self.tickPaddingPrepare()

        TradeIdGenerator().init(CtpMarket_RequestId_Format,'redis')
        # self.registerTimedTask(self.queryDepthMarketData,timeout=5)

    # def queryDepthMarketData(self,*args):
    #     from mantis.trade.utils import get_contract_detail
    #     from vnpy.trader.vtObject import VtDepthMarketQueryReq
    #     gateway = self.mainEngine.getGateway('CTP')
    #     for symbol  in self.symbols:
    #         contract = get_contract_detail(symbol)
    #         if contract:
    #             req = VtDepthMarketQueryReq()
    #             req.symbol = symbol
    #             req.exchange = contract.exchange
    #             req.request_id = TradeIdGenerator().next_id()
    #             gateway.queryDepthMarketData(req)
    #             time.sleep(1)
    #
    #             req = VtContractCommissionRateData()
    #             req.symbol = symbol
    #             req.exchange = contract.exchange
    #             req.request_id = TradeIdGenerator().next_id()
    #             gateway.queryCommissionRate(req)
    #             time.sleep(1)

    def queryContractTradeParameters(self,*args):
        from mantis.trade.utils import get_contract_detail
        from vnpy.trader.vtObject import VtDepthMarketQueryReq
        gateway = self.mainEngine.getGateway('CTP')
        for symbol in self.symbols:
            contract = get_contract_detail(symbol)
            if contract:
                req = VtDepthMarketQueryReq()
                req.symbol = symbol
                req.exchange = contract.exchange
                req.request_id = TradeIdGenerator().next_id()
                gateway.queryDepthMarketData(req)
                time.sleep(1)

                req = VtContractCommissionRateData()
                req.symbol = symbol
                req.exchange = contract.exchange
                req.request_id = TradeIdGenerator().next_id()
                gateway.queryCommissionRate(req)
                time.sleep(1)

    def tickPaddingPrepare(self):
        """填充Tick空洞"""
        redis = instance.datasourceManager.get('redis').conn
        symbols = self.contracts.keys()
        for symbol in symbols:
            tick_key = CtpMarketSymbolTickFormat.format(symbol)
            dict_ = redis.hgetall(tick_key)
            tick = VtTickData()
            tick.__dict__ = dict_
            self.contract_ticks[symbol] = {'last':tick,}

    def initCommandChannels(self):
        """默认不启用通道"""
        pass

    def handle_channel_read(self,data,ctx):
        pass

    def processLogEvent(self, event):
        print event

    def processErrorEvent(self, event):
        """
        处理错误事件
        错误信息在每次登陆后，会将当日所有已产生的均推送一遍，所以不适合写入日志
        """
        error = event.dict_['data']
        print u'错误代码：%s，错误信息：%s' % (error.errorID, error.errorMsg)

    def stop(self):
        super(MarketService, self).stop()
        self.mainEngine.exit()
        if self.active:
            self.active = False
            # self.thread.join()

    def join(self):
        self.thread.join()

    # def subscribe(self, *symbols):
    #     for symbol in symbols:
    #         if not self.symbols.has_key(symbol):
    #             req = VtSubscribeReq()
    #             req.symbol = symbol
    #             self.mainEngine.subscribe(req, self.gatewayName)  # CTP
    #             self.symbols[symbol] = symbol
    #
    # def unsubscribe(self, *symbols):
    #     for s in symbols:
    #         if s in self.symbols.keys():
    #             del self.symbols[s]

    def getSymbols(self):
        return list(self.contracts.keys())

    def procecssTickEvent(self, event):
        """处理行情事件"""
        tick = event.dict_['data']
        ticks =[]

        # ticks = self.doTickPadding(tick)
        ticks.append(tick)
        ticks = self.filterTicks(ticks)
        for tick in ticks:
            # 生成datetime对象
            if not tick.datetime:
                # tick.datetime = datetime.strptime(' '.join([tick.date, tick.time]), '%Y%m%d %H:%M:%S.%f')
                tick.service = self.getServiceType() + '.' + self.getServiceId()

            self.queue.put(tick)

    def initFilters(self):
        from mantis.fundamental.utils.importutils import import_class
        for clsname in self.cfgs.get('ctp_tick_filters', []):
            cls = import_class(clsname)
            filter = cls()
            self.tick_filters.append(filter)

    def filterTicks(self, ticks):
        """将tick传递给所有的filter，但如果前一个filter返回None，
        则终止传递到下一个filter，也意味着tick无效
        一次处理多个tick
        """
        result =[]
        for tick in ticks:
            for f in self.tick_filters:
                tick = f.validate(tick)
                if not tick:
                    break
            if tick:
                result.append(tick)
        return result

    def registerEvent(self):
        """注册事件监听"""
        self.ee.register(EVENT_TICK, self.procecssTickEvent)
        self.ee.register(EVENT_LOG, self.processLogEvent)
        self.ee.register(EVENT_ERROR, self.processErrorEvent)
        self.ee.register(EVENT_CONTRACT, self.processContractEvent)
        self.ee.register(EVENT_DATA,self.processDataEvent)
        # self.ee.register(EVENT_CONTRACT_COMMISSION, self.processContractCommissionEvent)
        # self.ee.register(EVENT_DEPTH_MARKET_DATA,self.processDepthMarketDataEvent)

    def subscribeSymbols(self):
        """支持两种合约名称定义：
           1. 列表 'a,b,c,..'
           2. 文件名 file:./_ctp_contracts.txt
        """
        text = self.cfgs.get('subscribe_symbols', '')
        symbols = []
        if text.count(':'):
            _,filename = text.split(':')
            lines = open(filename).readlines()
            lines = filter(lambda s:s.strip(),lines)
            symbols = map(lambda  s: s.split()[0],lines)
        else:
            symbols = self.cfgs.get('subscribe_symbols', '').split(',')
            symbols = map(str.strip, symbols)

        if symbols:
            print time.asctime(), 'Prepare Subscribing {} symboles .. '.format(len(symbols))
            for symbol in symbols:
                req = VtSubscribeReq()
                req.symbol = symbol
                self.mainEngine.subscribe(req, self.gatewayName)

        self.symbols = symbols


    # def subscribeAllContracts(self):
    #     print 'Total {} Contracts To Be Subscribed..'.format(len(self.contracts.keys()))
    #     for symbol in self.contracts.keys():
    #         req = VtSubscribeReq()
    #         req.symbol = symbol
    #         self.mainEngine.subscribe(req,'CTP')  # CTP

    def filterContract(self,contract):
        """过滤合约"""
        import re
        # 套利合约名称过滤 ； 过长文件合约过滤
        # name = contract.vtSymbol
        # if name.count('-') or name.count('&') or len(name) >8:
        #     # print 'Skip Contract:',name
        #     return None
        from mantis.trade.utils import verify_contract_name
        # 套利合约名称过滤 ； 过长文件合约过滤
        name = contract.vtSymbol
        name = verify_contract_name(name)
        if not name:
            return None

        # 生成 合约相关的交易时间段字段 ( regex 过滤出产品类型前缀)
        m = re.findall('^([A-Za-z]{1,3})\d{2,5}', name)
        if not m:
            return None
        contract.marketProduct = m[0].upper() # IF,AU,CU ,...
        return contract


    def processDepthMarketDataEvent(self,event):
        """"""
        data = event.dict_['data']
        self.logger.debug('== processDepthMarketDataEvent()')
        print data.__dict__
        redis = instance.datasourceManager.get('redis').conn
        symbol = data.symbol
        data = json.dumps(data.__dict__)
        print data
        print redis.hset(CtpDepthMarketDataListKey, symbol,data)
        print '-- processDepthMarketDataEvent -- END --'

    def processContractCommissionEvent(self,event):
        """交易手续费"""
        data = event.dict_['data']
        self.logger.debug('== processContractCommissionEvent()')
        print data.__dict__
        symbol = data.symbol
        data = json.dumps(data.__dict__)
        redis = instance.datasourceManager.get('redis').conn
        redis.hset(CTAContractCommissionListKey, symbol,data)

    def processDataEvent(self,event):
        data = event.dict_['data']
        if isinstance(data,VtContractCommissionRateData):
            self.processContractCommissionEvent(event)
        elif isinstance(data,VtDepthMarketData):
            self.processDepthMarketDataEvent(event)

    def processContractEvent(self, event):
        """处理合约事件
           连接交易系统之后,会通过此接口接收到CTP所有当前合约
        """
        contract = event.dict_['data']
        if  self.filterContract(contract):
        # if  1:
            self.contracts[contract.vtSymbol] = contract #json.dumps(contract.__dict__)
        # print 'contract.last:',contract.last
        if contract.last:
            # start contract subscribe
            # print time.asctime(),' Contract Last is True, Go To Subscribe .. '
            # symbols = self.cfgs.get('subscribe_symbols','').split(',')
            # symbols = map(str.strip,symbols)
            # if symbols:
            #     for symbol in symbols:
            #         req = VtSubscribeReq()
            #         req.symbol = symbol
            #         self.mainEngine.subscribe(req, self.gatewayName)
            # else:
            #     self.subscribeAllContracts()
            f = open('_ctp_contracts.txt', 'w')
            # print self.contracts.values()
            names = sorted(self.contracts.keys(), lambda x, y: cmp(x, y))
            contracts =OrderedDict()
            for name in names:
                c = self.contracts[name]
                # d = json.loads(c)
                f.write(c.symbol + ' ')
                f.write(c.name.encode('utf-8'))
                f.write('\n')
                contracts[name] = json.dumps(c.__dict__)
            f.close()

            redis = instance.datasourceManager.get('redis').conn

            redis.hmset(CTAContractListKey, contracts)

            self.registerTimedTask(self.queryContractTradeParameters,timeout=5)
            # self.queryDepthMarketData()



    def threadDataFanout(self):
        """运行插入线程"""
        import traceback
        while self.active:
            try:
                # print 'current tick queue size:', self.queue.qsize()
                # dbName, collectionName, d = self.queue.get(block=True, timeout=1)
                tick = self.queue.get(block=True, timeout=1)
                symbol = tick.vtSymbol

                #调试，仅允许调试合约发送

                if self.cfgs.get('debug_symbols',[]):
                    if self.cfgs.get('debug_symbols').count(symbol) == 0:
                        continue

                dt = datetime.datetime.strptime(' '.join([tick.date, tick.time]),'%Y%m%d %H:%M:%S.%f')
                tick.ts  = datetime_to_timestamp( dt )  # 合约生成时间
                tick.ts_host = int(time.time())         # 主机系统时间
                tick.mp = self.contracts.get(symbol).marketProduct # IF,AU,CU,..

                # 传播到下级服务系统
                jsondata = json.dumps(tick.__dict__)
                self.dataFanout('switch0', jsondata, symbol=symbol)

                # -- cache current tick into redis ---
                key_name = CtpMarketSymbolTickFormat.format(symbol = tick.vtSymbol)
                redis = instance.datasourceManager.get('redis').conn
                redis.hmset(key_name,tick.__dict__)

                #-- cache for query --
                self.ticks_counter += 1
                if len(self.ticks_samples) > 2:
                    del self.ticks_samples[0]
                self.ticks_samples.append(tick.__dict__)

            except Exception as e:
                # self.logger.error( str(e) )
                # traceback.print_exc()
                pass

    def doTickPadding(self,tick):
        """
        根据两次tick之间的时间间隔判断是否进行填充
        当前系统timestamp与tick.host_ts的时间差是否大于时间限定

        """
        symbol = tick.vtSymbol
        last = self.contract_ticks.get(symbol)
        if not last:
            self.contract_ticks[symbol] = tick
            return []
        result =[]
        if tick.ts - last.ts > 10:
            for ts in range(last.ts,tick.ts,10):
                if ts  == last.ts:
                    continue # skip first
                new = copy.copy(last)
                new.ts = ts
                new.ts_host = int(time.time())
                new.source = 'pad'
                sdatetime = datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d %H:%M:%S.%f')
                new.date,new.time =sdatetime.split(' ')
                result.append(new)
        return result


@singleton
class TradeIdGenerator(object):
    """交易请求流水号生成器"""
    def __init__(self):
        self.redis = None
        self.key = ''

    def init(self,key,datasource='redis'):
        """从db/redis加载当前的值"""
        self.key = key
        self.redis = instance.datasourceManager.get(datasource).conn
        return self

    def next_id(self):
        """提供策略使用的request-id"""

        id = self.redis.incrby(self.key,1)
        return id
