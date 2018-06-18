#coding:utf-8

import json
from collections import OrderedDict
from mantis.fundamental.utils.useful import hash_object,object_assign
from mantis.trade.types  import TradeAccountInfo,TradeUserInfo,TradeSubAccountInfo

DevelopUserStrategyKeyPrefix ='development.users.{user}.strategies.{strategy_name}'
TradeUserStrategyKeyPrefix = 'trade.users.{user}.strategies.{strategy_name}'

class StrategyRunMode(object):
    Null        = 'null'
    Development = 'dev'
    Product = 'product'

class StrategyTask(object):
    NAME = 'strategy_task'
    def __init__(self):
        self.trade_account = TradeAccountInfo()
        self.trade_sub_account = TradeSubAccountInfo()
        self.trade_user = TradeUserInfo()
        self.strategy = StrategyInfo()
        self.start_time = 0

    # def update(self,cfgs,prefix=''):
    #     if prefix:
    #         prefix+='.'
    #
    #     prefix+=StrategyTask.NAME+'.'
    #
    #     self.trade_account.update(cfgs,prefix)
    #     self.trade_sub_account.update(cfgs,prefix)
    #     self.trade_user.update(cfgs,prefix)
    #     self.strategy.update(cfgs,prefix)
    #
    # def dict(self,prefix=''):
    #     if prefix:
    #         prefix+='.'
    #     prefix += StrategyTask.NAME
    #
    #     result = OrderedDict()
    #
    #     result.update(self.trade_account.dict(prefix= prefix))
    #     result.update(self.trade_sub_account.dict(prefix= prefix))
    #     result.update(self.trade_user.dict(prefix= prefix))
    #     result.update(self.strategy.dict(prefix= prefix))
    #     return result

    def loads(self,cfgs):
        self.trade_account.loads(cfgs.get('trade_account',{}))
        self.trade_sub_account.loads(cfgs.get('trade_sub_account',{}))
        self.trade_user.loads(cfgs.get('trade_user',{}))
        self.strategy.loads(cfgs.get('strategy',{}))

    def dumps(self):
        result=dict(trade_account=self.trade_account.dumps(),
                    trade_sub_account = self.trade_sub_account.dumps(),
                    trade_user = self.trade_user.dumps(),
                    strategy=self.strategy.dumps()
                    )
        return result

class StrategyInfo(object):
    NAME = 'strategy'
    def __init__(self):
        self.strategy_id = '' # base64( md5( 策略名称 +策略代码) )
        self.name = ''
        self.codes = {}      # 策略代码 , { name:content } ,例如: 'main.py':'xxxxx'
        self.sum = ''       # 代码checksum
        self.params ={}     # 策略运行参数
        self.configs ={}
        self.extras ={}

    # def update(self,cfgs,prefix=''):
    #     if prefix:
    #         prefix+='.'
    #     prefix+=StrategyInfo.NAME + '.'
    #     self.strategy_id    = cfgs.get(prefix+'strategy_id','')
    #     self.code           = cfgs.get(prefix+'code','')
    #     self.sum            = cfgs.get(prefix+'sum','')
    #     self.params         = cfgs.get(prefix+'params','') # 需要json decode
    #     self.configs        = cfgs.get(prefix+'configs','')
    #     self.extras         = cfgs.get(prefix+'extras','')
    #
    #     if self.params:
    #         self.params = json.loads(self.params)
    #
    #     if self.configs:
    #         self.configs = json.loads(self.configs)
    #
    #     if self.extras:
    #         self.extras = json.loads(self.extras)
    #
    # def dict(self,prefix=''):
    #     if prefix:
    #         prefix+='.'
    #     prefix+=StrategyInfo.NAME+'.'
    #     return hash_object(self,prefix,excludes=['NAME'])

    def loads(self, cfgs):
        object_assign(self,cfgs)

    def dumps(self):
        result = hash_object(self)
        return result


if __name__ == '__main__':
    st = StrategyTask()
    print st.dict().keys()