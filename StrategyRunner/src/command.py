# coding:utf-8

import os,os.path
import base64
import yaml
import json
from mantis.fundamental.application.app import  instance
from mantis.trade.strategy import StrategyTask
from mantis.trade.constants import *

MAIN_FILE_CONTENT='''# coding:utf-8

# context: Context
context = None

def init(ctx):
    #  See : demo/config.yaml
    print ctx.task.strategy.configs

def start(ctx):
    print 'strategy: start()..'
    ctx.controller.setTimer(user='ctp',timeout=2)
    symbols = ctx.task.strategy.params.get('sub_ticks','').split(',')
    # ctx.controller.subTicks(symbols[0])
    ctx.controller.subBars(symbols[0],'5m')

def stop(ctx):
    print 'strategy: stop()..'


def onTick(tick,ctx):
    """
    tick - mantis.trade.types.TickData
    """
    print 'strategy: onTick()..'
    print 'tick:',tick.symbol
    print 'tick.data', tick.data

def onTrade(trade,ctx):
    print 'strategy: onTrade()..'

def onBar(bar,ctx):
    """
    bar - mantis.trade.types.BarData()
    """
    print 'strategy: onBar()..'
    print 'bar:',bar.symbol,bar.scale
    print 'bar.data:',bar.data

def onTimer(timer,ctx):
    # print 'strategy: onTimer()..',timer.timeout,timer.user
    pass

'''

STRATEGY_CONFIG_FILE="""
# config.yaml
# 策略的运行配置参数

name: 'demo'
user: 'scott'           # 交易用户名称
quotas:                 # 分配的资金账号
  - name:   'q001'      # 配额名称
    account: 'htqh-01' # 资金账户名称
    product: 'future'   # 期货、股票
    limit:  2000000     # 资金最大配额
strategy:
  id: ''
  configs:      # 此处由开发人员自行配置
    sub_ticks: 'AP810,RM809'
    sub_bar_1m: 'AP810,RM809'
    sub_bar_5m: 'AP810,RM809'

  codes:
  sum:
  
"""

DevelopUserQuotaPrefix = "development.users.{user}.quotas."
TradeUserQuotaPrefix = "trade.users.{user}.quotas."

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

def pull(strategy_name,strategy_key=DevelopUserStrategyKeyPrefix):
    """
    pull strategy stuff to local from reposistory
    :param name:
    :param strategy_key
    :return:
    """
    redis = instance.datasourceManager.get('redis').conn

    # - 1.加载用户策略 -
    key = strategy_key.format(user=get_username(),strategy_name=strategy_name)
    cfgs = redis.hgetall(key)
    if not cfgs:
        print 'Error: Strategy:{} not be found.'.format(strategy_name)
        return

    # cfgs['strategy'] = json.loads(cfgs['strategy'])
    cfgs['strategy'] = yaml.safe_load(cfgs['strategy'])

    # - 2.加载用户配额设置 -
    if strategy_key == DevelopUserStrategyKeyPrefix:
        key = DevelopUserQuotaPrefix
    else:
        key = TradeUserQuotaPrefix

    key = key.format(user = get_username()) + '*'
    names = redis.keys(key)

    cfgs['quotas'] = []

    for name in names:
        # qname = name.split(key)[1]  # quota's name
        quota = redis.hgetall(name)
        cfgs['quotas'].append(quota)

    # -- end --

    task = StrategyTask()
    task.loads(cfgs)

    # 创建策略的代码和配置文件
    path = os.path.join(instance.getHomePath(), 'src/strategies', strategy_name)
    if not os.path.exists(path):
        os.mkdir(path)
    # 写入文件
    for moduleName,content in task.strategy.codes.items():
        filename = os.path.join(path,moduleName)
        fp = open(filename,'w')
        content = base64.b64decode(content)
        fp.write(content)
        fp.close()
    # 删除 codes 属性
    if cfgs.get('strategy',{}).has_key('codes'):
        del cfgs.get('strategy',{})['codes']

    # 写入配置文件 config.yaml
    stream = yaml.dump(cfgs,default_flow_style=False,allow_unicode=True,indent =True)
    filename = os.path.join(path,'config.yaml')
    fp = open(filename,'w')
    fp.write(stream)
    fp.close()

    path = os.path.join(instance.getHomePath(), 'src/strategies', strategy_name)
    print 'Strategy: {} Pull Successful. \n{}'.format(strategy_name,path)

def upload(name,strategy_key=DevelopUserStrategyKeyPrefix):
    """
    put all stragegy files into repository
    将本地的策略推送到仓库
    :param name:
    :param UserStrategyKeyPrefix
    :return:
    """
    redis = instance.datasourceManager.get('redis').conn

    key = strategy_key.format(user=get_username(),strategy_name=name)
    path = os.path.join(instance.getHomePath(), 'src/strategies', name)
    filename = os.path.join(path,'config.yaml')

    cfgs = yaml.load(open(filename).read())
    if not cfgs:
        print 'Error: config.yaml not be found.'
        return

    # 扫描本地策略相关的文件,多文件读取base64编码之后塞入 .codes 属性
    files = os.listdir(path)
    codes = {}
    for file_ in files:
        content = open( os.path.join(path,file_),'r').read()
        content = base64.encodestring(content)
        codes[file_] = content

    cfgs['strategy']['codes'] = codes
    cfgs['strategy'] = json.dumps(cfgs['strategy'])

    # 删除 quotas
    quotas = {}
    if cfgs.has_key('quotas'):
        quotas = cfgs['quotas']
        del cfgs['quotas']
    # 写入用户的策略配置
    redis.hmset(key,cfgs)

    # 单独写入用户的配额参数

    dict_ = {}
    for q in quotas:
        qname = TradeAdapterServiceIdFormat.format(product = q['product'],account= q['account'])
        if strategy_key == DevelopUserStrategyKeyPrefix:
            key = DevelopUserQuotaPrefix
        else:
            key = TradeUserQuotaPrefix
        key = key.format(user = get_username()) + qname
        redis.hmset(key, q)

    print 'Strategy: {}  UpLoad Successful.'.format(name)

def run_local_name(name,KeyPrefix,service):
    """
    > run s1
    :param name:
    :param KeyPrefix:
    :return:
    """
    # run local strategy
    # 本地开发运行策略
    main = service
    main.controller.loadStrategy(name) # 加载策略目录下的指定策略名称的启动模块

    # 可以启动进程但不运行策略
    if  main.cfgs.get('auto_start',True):
        main.controller.open() # 开始
    print 'Strategy: {}  start running..'.format(name)


def run_server_strategy_id(sid,service):
    """
    > run --remote s1
    :param sid:
    :return:
    """
    # 运行线上的策略 ,  策略存储在交易用户的策略仓库中
    # 拉取线上(redis)中的策略信息到本地策略目录,并运行
    KeyPrefix = TradeUserStrategyKeyPrefix
    # run strategy in repository
    pull(sid,KeyPrefix)
    run_local_name(sid,KeyPrefix,service)
