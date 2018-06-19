# coding:utf-8

import os,os.path
import base64
import yaml
import json
from mantis.fundamental.application.app import  instance
from mantis.trade.strategy import DevelopUserStrategyKeyPrefix,TradeUserStrategyKeyPrefix
from mantis.trade.strategy import StrategyTask,StrategyInfo
from mantis.trade.types import TradeUserInfo,TradeSubAccountInfo,TradeAccountInfo

MAIN_FILE_CONTENT="""
#coding: utf-8

context = None  #

def init(ctx):
    pass

def start(ctx):
    pass

def stop(ctx):
    pass


def onTick(tick,ctx):
    pass

def onTrade(trade,ctx):
    pass

def onBar(bar,ctx):
    pass

def onTimer(timer,ctx):
    pass 

"""

STRATEGY_CONFIG_FILE="""
# config.yaml
# 策略的运行配置参数

name: 'demo'

trade_account:
  product_class: 'FUTURE'
  gateway:  'CTP'
  broker: ''
  user: ''
  password: ''
  market_server_addr: ''
  trade_server_addr: ''
  auth_code: ''
  user_product_info: ''

trade_sub_account:
  account: ''
  fund_limit: 0

trade_user:
  user: ''
  password: ''

strategy:
  strategy_id: ''
  params:
  configs:
  extras:
  
"""

# UserStrategyKeyPrefix = DevelopUserStrategyKeyPrefix

def get_username():
    return 'scott'

def create(name,UserStrategyKeyPrefix=DevelopUserStrategyKeyPrefix):
    """创建新策略
    检测当前用户下是否存在相同名称的策略
    在strateies目录下创建name的包,创建main.py,config.yaml文件
    :param name
    :param UserStrategyKeyPrefix

    > create strategy_name
    """
    redis = instance.datasourceManager.get('redis').conn
    key = UserStrategyKeyPrefix.format(user=get_username(),
                                              strategy_name=name)
    items = redis.keys(key)
    if items:
        print 'Error: Strategy: ( {} ) Exists In Redis.'.format(name)
        return False

    # 依次创建策略包和相关文件
    path = os.path.join(instance.getHomePath(),'src/strategies',name)
    if os.path.exists(path):
        print 'Error: Strategy ( {} ) Exists In Local Directory.'.format(name)
        return

    os.mkdir(path)

    filename = os.path.join(path,'__init__.py')
    fp = open(filename,'w')
    fp.close()
    filename = os.path.join(path, 'main.py')
    fp = open(filename, 'w')
    fp.write(MAIN_FILE_CONTENT)
    fp.close()
    filename = os.path.join(path,'config.yaml')
    fp = open(filename,'w')
    fp.write(STRATEGY_CONFIG_FILE)
    fp.close()

    print 'Stragegy: {} Created Successful. \nPath:{}'.format(name,path)
    return True


def list(name='',UserStrategyKeyPrefix=DevelopUserStrategyKeyPrefix):
    """
    列出所有隶属于开发用户的策略列表
    :param name:
    :param UserStrategyKeyPrefix
    :return:
    """
    redis = instance.datasourceManager.get('redis').conn
    key = UserStrategyKeyPrefix.format(user=get_username(),strategy_name='*')
    items = redis.keys(key)
    for item in items:
        name = item.split('.')[-1]
        print 'Strategy: {} '.format(name)


def remove(name,UserStrategyKeyPrefix=DevelopUserStrategyKeyPrefix):
    """
    删除仓库和本地项目
    :param name:
    :param UserStrategyKeyPrefix
    :return:
    """
    redis = instance.datasourceManager.get('redis').conn
    key = UserStrategyKeyPrefix.format(user=get_username(),strategy_name=name)
    cfgs = redis.hgetall(key)
    if not cfgs:
        print 'Error: Strategy:{} not be found.'.format(name)
        return

    redis.delete(key)
    print 'Remove Strategy:{} Successful.'.format(name)

def pull(name,UserStrategyKeyPrefix=DevelopUserStrategyKeyPrefix):
    """
    pull strategy stuff to local from reposistory
    :param name:
    :param UserStrategyKeyPrefix
    :return:
    """
    redis = instance.datasourceManager.get('redis').conn
    key = UserStrategyKeyPrefix.format(user=get_username(),
                                              strategy_name=name)
    cfgs = redis.hgetall(key)
    if not cfgs:
        print 'Error: Strategy:{} not be found.'.format(name)
        return

    task = StrategyTask()
    task.loads(cfgs)

    # 依次创建策略包和相关文件
    path = os.path.join(instance.getHomePath(), 'src/strategies', name)
    os.mkdir(path)

    # pull all strategy-codes from repository down to local project .
    for moduleName,content in task.strategy.codes.items():
        filename = os.path.join(path,moduleName)
        fp = open(filename,'w')
        content = base64.b64decode(content)
        fp.write(content)
        fp.close()

    if cfgs.get('strategy',{}).has_key('codes'):
        del cfgs.get('strategy',{})['codes']

    stream = yaml.dump(cfgs,default_flow_style=False)
    filename = os.path.join(path,'config.yaml')
    fp = open(filename,'w')
    fp.write(stream)
    fp.close()

    path = os.path.join(instance.getHomePath(), 'src/strategies', name)
    print 'Strategy: {} Pull Successful. \n{}'.format(name,path)

def upload(name,UserStrategyKeyPrefix=DevelopUserStrategyKeyPrefix):
    """
    put all stragegy files into repository
    将本地的策略推送到仓库
    :param name:
    :param UserStrategyKeyPrefix
    :return:
    """
    redis = instance.datasourceManager.get('redis').conn
    key = UserStrategyKeyPrefix.format(user=get_username(),strategy_name=name)

    path = os.path.join(instance.getHomePath(), 'src/strategies', name)
    filename = os.path.join(path,'config.yaml')

    cfgs = yaml.load(open(filename).read())
    if not cfgs:
        print 'Error: config.yaml not be found.'
        return

    # 扫描本地策略相关的文件
    # 多文件读取base64编码之后塞入 .codes 属性
    files = os.listdir(path)
    codes = {}
    for file_ in files:
        content = open( os.path.join(path,file_),'r').read()
        content = base64.encodestring(content)
        codes[file_] = content

    cfgs['strategy']['codes'] = codes
    cfgs['trade_account'] = json.dumps(cfgs['trade_account'])
    cfgs['trade_sub_account'] = json.dumps(cfgs['trade_sub_account'])
    cfgs['trade_user'] = json.dumps(cfgs['trade_user'])
    cfgs['strategy'] = json.dumps(cfgs['strategy'])

    # 推送到redis 策略仓库
    redis.hmset(key,cfgs)

    print 'Strategy: {}  UpLoad Successful.'.format(name)

def run_local_name(name,KeyPrefix):
    """
    > run --name=s1
    :param name:
    :param KeyPrefix:
    :return:
    """
    # run local strategy
    # 本地开发运行策略
    main = instance.serviceManager.get('main')
    main.controller.loadStrategy(name) # 加载策略目录下的指定策略名称的启动模块
    main.controller.open() # 开始
    print 'Strategy: {}  Begin To Run..'.format(name)


def run_server_strategy_id(sid):
    """
    > run --sid=s1
    :param sid:
    :return:
    """
    # 运行线上的策略 ,  策略存储在交易用户的策略仓库中
    # 拉取线上(redis)中的策略信息到本地策略目录,并运行
    KeyPrefix = TradeUserStrategyKeyPrefix
    # run strategy in repository
    pull(sid,KeyPrefix)
    run_local_name(sid,KeyPrefix)
