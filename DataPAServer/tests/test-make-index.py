#coding:utf-8

from datetime import datetime as DateTime,timedelta as TimeDelta,time as Time
import time
import pandas as pd
import numpy as np
from dateutil.parser import parse
from dateutil.rrule import *
import pymongo
import  mantis.trade.kline as kline

conn = pymongo.MongoClient('s103',27017)

kline.mongodb_conn = conn

def init_index_ctp_tick(symbols):
    for symbol in symbols:
        coll = conn['Ctp_Tick'][symbol]
        coll.create_index([ ('datetime',pymongo.ASCENDING,),('seq',pymongo.ASCENDING)])
        coll.create_index([('datetime', pymongo.DESCENDING,), ('seq', pymongo.DESCENDING)])
        coll.create_index([('datetime',pymongo.ASCENDING)])

symbols ='m1901,RM901,y1901,c1901,AP901,CF901,a1901,hc1901,rb1901'
init_index_ctp_tick(symbols.split(','))