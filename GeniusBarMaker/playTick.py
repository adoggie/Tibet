#coding:utf-8

"""
playTick.py
模拟测试Tick从mongodb读取 , 并发送到 redis队列 ，等待 GeniusBarMaker 读取并处理

"""


import json
import copy
import json
import time,datetime
import traceback
import threading
from collections import OrderedDict
from functools import partial
from dateutil.parser import  parse
import requests

from mantis.fundamental.redis.broker import MessageBroker
from mantis.fundamental.utils.useful import object_assign ,hash_object,singleton
import config


symbol = 'm1909'
dbname = 'Ctp_Tick'


broker = MessageBroker()
bar_channel_pub = None

db = config.db_conn[dbname]
coll = db[symbol]




def init_channel_pub():
    global bar_channel_pub

    host, port, db, passwd = config.broker_url.split(':')
    broker.init(dict(host=host, port=port, db=db, password=passwd))
    broker.open()

    channelname = 'ctp.tick.pub_' + symbol
    bar_channel_pub = broker.createPubsubChannel(channelname)
    bar_channel_pub.open()

def main():
    init_channel_pub()
    rs = coll.find()
    for r in list(rs):
        if r.has_key('DateTime_'):
            del r['DateTime_']
        del r['SaveTime']
        del r['_id']
        message = json.dumps(r)
        bar_channel_pub.publish_or_produce(message)
        time.sleep(.001)
        print 'pub tick..',symbol,r['DateTime']
    print 'play end..'

if __name__ == '__main__':
    if config.TEST:
        main()