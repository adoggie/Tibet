#coding:utf-8

from datetime import datetime as DateTime,timedelta as TimeDelta,time as Time
import time
import pandas as pd
import numpy as np
from dateutil.parser import parse
from dateutil.rrule import *
import pymongo
import  mantis.trade.kline as kline

conn = pymongo.MongoClient('localhost',27017)

kline.mongodb_conn = conn

def init_index_ctp_tick(symbols):
    for symbol in symbols:
        coll = conn['Ctp_Tick'][symbol]
        coll.create_index([ ('datetime',pymongo.ASCENDING,),('seq',pymongo.ASCENDING)])

init_index_ctp_tick(['AP901','m1901','ag1809'])