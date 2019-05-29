#coding:utf-8

from datetime import datetime as DateTime,timedelta as TimeDelta,time as Time
import time
import pandas as pd
import numpy as np
from dateutil.parser import parse
from dateutil.rrule import *

import pymongo
import  mantis.trade.kline as kline
import fire

# conn = pymongo.MongoClient('192.168.99.22',27018)

# kline.mongodb_conn = conn
dbs = ['Ctp_Tick', 'Ctp_Bar_1m', 'Ctp_Bar_3m', 'Ctp_Bar_5m', 'Ctp_Bar_15m', 'Ctp_Bar_30m', 'Ctp_Bar_1h']


class ShellCLi(object):
    def __init__(self,host='localhost',port=27017):
        self.host=host
        self.port= port
        self.conn = pymongo.MongoClient(self.host,self.port)
        kline.mongodb_conn = self.conn

    def init_index_ctp_tick(self,symbol):
        """初始化合约索引
        python tibet-shell init_index_ctp_tick m1901
        cat _ctp_contracts.txt | awk '{print $1}' | xargs -I {} python tibet-shell init_index_ctp_tick {}
        """
        coll = self.conn['Ctp_Tick'][symbol]
        print 'Create Index: {} ..'.format(symbol)
        coll.create_index([ ('datetime',pymongo.ASCENDING,),('seq',pymongo.ASCENDING)])

    def create_symbol_indexes(self):
        """
        创建所有DB的symbol的索引
        """
        for db in dbs:
            symbols = self.conn[db].collection_names()
            count = 1
            for symbol in symbols:
                print 'Collection: {} {}. {}'.format(db, count, symbol)
                count += 1
                coll = self.conn[db][symbol]
                coll.create_index([('datetime', pymongo.ASCENDING,), ('seq', pymongo.ASCENDING)])

    def remove_ctp_symbol(self,symbol):
        """
        删除指定合约的tick数据 ， k线数据 1m , 3m,5m,...

        """
        coll = self.conn['Ctp_Tick'][symbol]
        coll.drop()
        coll = self.conn['Ctp_Bar_1m'][symbol]
        coll.drop()
        coll = self.conn['Ctp_Bar_3m'][symbol]
        coll.drop()
        coll = self.conn['Ctp_Bar_5m'][symbol]
        coll.drop()
        coll = self.conn['Ctp_Bar_15m'][symbol]
        coll.drop()
        coll = self.conn['Ctp_Bar_30m'][symbol]
        coll.drop()
        coll = self.conn['Ctp_Bar_1h'][symbol]
        coll.drop()

    def remove_ctp_kline(self,symbol):
        """
        删除指定合约的 k线数据 1m , 3m,5m,...

        """
        # coll = self.conn['Ctp_Tick'][symbol]
        # coll.drop()
        coll = self.conn['Ctp_Bar_1m'][symbol]
        coll.drop()
        coll = self.conn['Ctp_Bar_3m'][symbol]
        coll.drop()
        coll = self.conn['Ctp_Bar_5m'][symbol]
        coll.drop()
        coll = self.conn['Ctp_Bar_15m'][symbol]
        coll.drop()
        coll = self.conn['Ctp_Bar_30m'][symbol]
        coll.drop()
        coll = self.conn['Ctp_Bar_1h'][symbol]
        coll.drop()

    def filter_unused_symbol(self,symbol):
        """过滤非正常采集的合约名称
        """
        from mantis.trade.utils import verify_contract_name
        if not verify_contract_name(symbol):
            # print symbol
            return symbol
        return ''

    def data_clean_remove_all_unused_symbols(self):
        # lines =map(str.strip,open(symbolfile).readlines())
        # symbols = map(lambda s:s.split()[0].strip(),lines)
        # print symbols
        dbs = ['Ctp_Tick', 'Ctp_Bar_1m', 'Ctp_Bar_3m', 'Ctp_Bar_5m', 'Ctp_Bar_15m', 'Ctp_Bar_30m', 'Ctp_Bar_1h']
        all ={}
        for db in dbs:
            print 'db:',db
            symbols = self.conn[db].collection_names()
            symbols = filter(lambda s:self.filter_unused_symbol(s),symbols)
            for s in symbols:
                all[s] = 1
        symbols = all.keys()

        print len(symbols)

        for db in dbs:
            count = 1
            for symbol in symbols:
                print 'Drop Collection: {} {}. {}'.format(db,count,symbol)
                count+=1
                if not db :
                    print 'db is None',db
                    break
                coll = self.conn[db][symbol]
                coll.drop()

    def ctp_data_clear(self,symbol,date):
        """清洗期货合约某一天的数据
            date - yyyy-mm-dd

            kline.data_clear_days('AP901','2018-7-27')
        """
        kline.mongodb_conn = self.conn
        kline.data_clear_days(symbol,date)

    def  make_trade_days(self,start,end,outfile='trade_days.txt',only_bis=True):
        """
        生成交易日历
        start - 开始日期 ; end - 结束日期 ; only_bis - 仅仅输出工作日
        交易日文件需放入 工程项目的 `etc/` 目录内，供k线处理程序访问
        """
        f = open(outfile,'w')
        days = pd.bdate_range(start,end)
        for day in days:
            print day.date(),day.weekday()+1
            f.write('{} {}\n'.format(str(day.date()),day.weekday()+1))
        f.close()

    def tickfix_add_field_flag(self):
        """为所有行情数据添加 flag字段
            flag: 0 - 可用 , 1 -不可用
        """
        symbols = self.conn['Ctp_Tick'].collection_names()
        count = 1
        for symbol in symbols:
            print 'Collection: {} {}. {}'.format('Ctp_Tick', count, symbol)
            count += 1
            coll = self.conn['Ctp_Tick'][symbol]
            coll.update_many(filter={},update={'$set': {'flag': 0}})


#https://google.github.io/python-fire/guide/

"""
python tibet-shell.py tickfix_add_field_flag --host 192.168.99.22 --port 27018

"""
if __name__ == '__main__':
    fire.Fire(ShellCLi)

# init_index_ctp_tick(['AP901'])