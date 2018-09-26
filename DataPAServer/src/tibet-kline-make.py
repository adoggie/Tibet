#coding:utf-8

"""
tibet-kline-make.py

在休盘时间自动计算交易时间段的 nmin k线数据
"""

import multiprocessing
from time import sleep
import logging
from logging.handlers import TimedRotatingFileHandler
from logging import StreamHandler

import time,os
from datetime import datetime ,timedelta as TimeDelta, time as Time
from dateutil.parser import parse
from dateutil.rrule import *
import  mantis.trade.kline as kline
from mantis.trade.types import TimeScale
import fire
import pymongo




class KlineCli(object):
    def __init__(self,host='localhost',port=27017,filename = 'ctp_contracts.txt',logfile='tibet-kline.log'):
        self.host=host
        self.port= port
        self.filename = filename
        self.logfile = logfile
        self.conn = pymongo.MongoClient(self.host,self.port)
        kline.mongodb_conn = self.conn
        # print self.host,self.port
        self.logger = self.init_logs()

    def init_logs(self):
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        handler = TimedRotatingFileHandler(self.logfile)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        handler = StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def log_print(self,msg):
        # print time.asctime(), msg
        self.logger.debug(msg)

    def make_min(self,symbol,date= str(datetime.now().date()) ):
        mins =  kline.get_day_trade_minute_line(symbol,parse(date))
        for min in mins:
            print 'Make Kline:',symbol, '1m',str(min)
            kline.make_min_bar(symbol, min, drop=True)
        # print mins

    def make_nmin(self,symbol,scale,date= str(datetime.now().date()) ):
        nmin = TimeScale.SCALES[scale]/TimeScale.MINUTE
        mins = kline.get_day_trade_nminute_line(symbol, nmin, parse(date))

        spaces = kline.get_trade_timetable_template(symbol)

        for min in mins:
            print 'Make Kline:', symbol,scale,str(min)
            space = kline.time_work_right_short(spaces, min)

            left = 0
            right = 1
            if len(space) == 3 and space[-1].count('*'):  # 开盘集合竞价
                left = 1
            if len(space) == 3 and space[-1].count('-'):  # 跨日时间
                right = 0
            kline.make_min_bar(symbol, min, scale, drop=True,leftMargin=left,rightMargin=right)
    # ----------------------------------------------------------------------
    def whenDayClose(self):
        """
        日盘结束 下午 15：35 执行当天'日k线'数据生成 ( 21:0 - 15:30 ) 跨日
        计算 指定合约的所有k线生成
        """
        self.log_print("Start K-line-Min Making..")
        date = datetime.now()
        self.make_kline_min(str(date.date()))
        self.log_print("End K-line-Min Made.")

        self.log_print('Start K-line-Day Making..')
        self.make_kline_day()
        self.log_print("End K-line-Day Made.")

        # WORK_START = Time(2, 35)  # 日盘启动和停止时间
        # WORK_END = Time(4, 0)
        #
        # running = False
        # while True:
        #     currentTime = datetime.now().time()
        #     # 判断当前处于的时间段
        #     if currentTime >= WORK_START and currentTime <= WORK_END :
        #         if not running:
        #             running = True
        #             self.log_print("Start K-line Making..")
        #             date = datetime.now() - TimeDelta(days=1)
        #             self.make_kline_min(str(date.date()))
        #             self.log_print("End K-line Made.")
        #
        #     else:
        #         running = False
        #     sleep(5)
        #     # self.log_print("keep Watching..")

    def whenNightClose(self):
        # 夜盘结束 凌晨 2: 35 开始运行
        # 计算所有合约 的 前一天的分钟k线(不包括日线)
        self.log_print("Start K-line-Min Making..")
        date = datetime.now() - TimeDelta(days=-1)
        self.make_kline_min(str(date.date()))
        self.log_print("End K-line-Min Made.")

    def make_kline_min(self,start = str(datetime.now().date()),days=1):
        """计算分钟k线 当天 9：00 - 隔日凌晨 2:30 之间的 数据"""

        symbols = self.get_subscribed_symbols()

        date = start
        if isinstance(date, str):
            date = parse(date)
        for _ in range(days):
            if kline.is_trade_day(date):
                date = date.replace(hour=0, minute=0, second=0, microsecond=0)
                today = date  # datetime.now()
                nextday = today + TimeDelta(days=1)
                self.ctp_data_clear(str(today.date()), str(nextday.date()))
                for symbol in symbols:
                    self.log_print('make_kline: {} '.format(symbol))
                    self.make_kline_min_symbol(symbol, str(date.date()))

            date = date + TimeDelta(days=1)






    def make_kline_min_symbol(self,symbol,date = str(datetime.now().date())):
        """计算指定日期某一合约的所有k线记录"""
        scales = ['3m', '5m', '15m', '30m', '60m']
        self.make_min(symbol, date)
        for scale in scales:
            self.make_nmin(symbol, scale, date)

    def get_subscribed_symbols(self):

        lines = open(self.filename).readlines()

        lines = filter(lambda s: s.strip(), lines)
        lines = filter(lambda s: s[0]!='#',lines)
        symbols = map(lambda s: s.split()[0], lines)
        return symbols

    def ctp_data_clear(self,start,end=''):
        """[start,end] 包含 end ，小与 < end+1"""
        symbols = self.get_subscribed_symbols()
        for symbol in symbols:
            self.ctp_data_clear_symbol(symbol,start,end)

    def ctp_data_clear_symbol(self,symbol,start,end=''):
        self.log_print('ctp_data_clear: {} {} - {}'.format(symbol,start,end))
        kline.data_clear_days(symbol, start,end)


    def ctp_data_check(self,start,end=''):
        symbols = self.get_subscribed_symbols()
        for symbol in symbols:
            self.ctp_data_check_symbol(symbol,start,end)

    def ctp_data_check_symbol(self,symbol,start,end=''):
        self.log_print('ctp_data_clear: {} {} - {}'.format(symbol,start,end))
        kline.data_clear_days(symbol, start,end,readonly=True)

    def make_kline_day(self,start = str(datetime.now().date()),days=1):
        """生成日线
            :param start - 开始日期
            :param days - 计算天数（期间非交易日跳过 ）

            值守服务应当在当日下午收盘之后即刻生成单日日线数据(15:15 - )
            某日线包含前一个交易日的夜盘 20:59 - 2:30 ，和当日日盘数据 9:00 - 15:15
        """
        symbols = self.get_subscribed_symbols()
        date = start
        if isinstance(date, str):
            date = parse(date)
        for _ in range(days):
            if kline.is_trade_day(date):
                date = date.replace(hour=0, minute=0, second=0, microsecond=0)
                for symbol in symbols:
                    self.make_kline_day_symbol(symbol,date)
            date =date+TimeDelta(days=1)

    def make_kline_day_symbol(self,symbol,date):
        """ 前日 夜盘  21：0 - 今日收盘 15：30 之间数据"""
        if isinstance(date,str):
            date = parse(date)
        self.log_print('make_kline_day: {} {}'.format(symbol, str(date.date())))
        self.ctp_data_clear_symbol(symbol,date)
        kline.make_day_bar(symbol, date)


#https://google.github.io/python-fire/guide/
"""
python tibet-kline-make.py ctp-data-clear 2018-8-13 --host 192.168.99.22 --port 27018 --filename ctp_contracts.txt
python tibet-kline-make.py ctp-data-check 2018-8-13 --host 192.168.99.22 --port 27018 --filename ctp_contracts.txt
python tibet-kline-make.py make_one m1901  --host 192.168.99.22 --port 27018

python tibet-kline-make.py make_kline_min 2018-8-13  --host 192.168.99.22 --port 27018
python tibet-kline-make.py make_kline_min_symbol AP810 2018-8-13  --host 192.168.99.22 --port 27018

python tibet-kline-make.py make_kline_day 2018-8-13  --host 192.168.99.22 --port 27018
python tibet-kline-make.py make_kline_day_symbol AP810 2018-8-13  --host 192.168.99.22 --port 27018

python tibet-kline-make.py whenDayClose  --host 192.168.99.22 --port 27018
python tibet-kline-make.py whenNightClose  --host 192.168.99.22 --port 27018

"""
if __name__ == '__main__':
    fire.Fire(KlineCli)















