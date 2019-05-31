#coding:utf-8

import sys,os,os.path,traceback,time,datetime


REAL = True  # 实盘数据还是历史模拟数据
TEST = True



host='192.168.1.252'
host='192.168.129.134'
db_host= host

db_conn = None
broker_url = '{}:6379:0:'.format(host)

def init_db(host='127.0.0.1', port=27017, date=None):
    """
    date : str 默认为当日
    """
    global db_conn
    from pymongo import MongoClient
    db_conn = MongoClient(host, port)

init_db(db_host)