#coding:utf-8

import time
import datetime
import dateutil.parser as dateparser

def str_to_timestamp(time_str):

    # OR: dt = time.strptime(datetimestring, fmt)
    # print time_str
    try:
        dt = dateparser.parse(time_str)
        return time.mktime(dt.timetuple())
    except:
        return 0

# datetimestring = 'Fri, 08 Jun 2012 22:40:26 GMT'
# str_to_timestamp(datetimestring)

def current_datetime_string():
    return timestamp_to_str(timestamp_current())

def timestamp_current():
    return int(time.time())

def timestamp_to_str(ts, fmt='%Y-%m-%d %H:%M:%S'):
    return time.strftime(fmt, time.localtime(ts))

def datetime_to_timestamp(dt):
    return int(time.mktime(dt.timetuple()))

def get_across_days(start,end):
    """ 计算 start,end （timestamp) 跨越的日期(天)集合
    """
    s = datetime.datetime.fromtimestamp(start)
    e = datetime.datetime.fromtimestamp(end)
    days = e.date() - s.date()
    result=[]
    s = datetime.datetime(s.year,s.month,s.day)
    for _ in range(days.days+1):
        day = s + datetime.timedelta(_)
        result.append(day)
    return result