# coding: utf-8

# ticks data generator
# =====================
# 1. read tick from mongodb
# 2. publish tick into ctp_tick_{symbol}

import os,os.path
import yaml
import json
from mantis.fundamental.redis.datasource  import Datasource
from mantis.trade.constants import *

#资金账号
# product - 期货/股票/其他

KEYACC_DEV = DevelopAccountNameFormat
KEYACC_PRD = TradeAccountNameFormat


path = os.path.abspath(__file__)
path = '../etc/settings.yaml'
cfgs = yaml.load(open(path).read())

ds = Datasource(cfgs.get('datasources')[2]) # redis
ds.open()

path = './sample.yaml'
cfgs = yaml.load(open(path).read())

for acc in cfgs.get('accounts'):
    key = KEYACC_DEV.format(product=acc['product'],account=acc['name'])
    ds.conn.hmset(key,acc)
    key = KEYACC_PRD.format(product=acc['product'], account=acc['name'])
    ds.conn.hmset(key, acc)

# 写入用户资金配额
KEYACC = DevelopUserAccountQuotaFormat


"""
配额列表，key 是 产品类型+资金账户名称 的组合
future.htqh-01	{'account': 'htqh-01', 'product': 'future', 'quota': 100000}

"""

for cfg in cfgs.get('users'):
    user = cfg['name']
    quotas = cfg['quotas']
    dict_ = {}
    for q in quotas:
        name = TradeAdapterServiceIdFormat.format(product=q['product'],account= q['account'])
        key = KEYACC.format(user=cfg['name'],account= name)
        ds.conn.hmset(key,q)

