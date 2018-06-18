# coding: utf-8

# ticks data generator
# =====================
# 1. read tick from mongodb
# 2. publish tick into ctp_tick_{symbol}

import os,os.path
import yaml
import json
from mantis.fundamental.nosql.mongo import Datasource
from mantis.fundamental.redis.broker import MessageBroker
from vnpy.trader.vtObject import VtTickData

symbol = 'cu1809'
dbname = 'Ctp_Ticks'

path = os.path.abspath(__file__)
path = '../etc/settings.yaml'
cfgs = yaml.load(open(path).read())

ds = Datasource(cfgs.get('datasources').get('mongodb'))
ds.open()
broker =MessageBroker()
pubchan = broker.createPubsubChannel('ctp_tick_{}'.format(symbol))


collname = symbol

# read some ticks
ticks = []

for tick in ticks :
    # modify tick time to current time

    # publish out
    data = json.dumps(tick.__dict__)
    pubchan.publish_or_produce(data)
