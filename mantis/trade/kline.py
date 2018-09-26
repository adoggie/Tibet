#coding:utf-8


"""
mongodb api ref:
https://docs.mongodb.com/manual/reference/method/db.collection.find/
"""
from collections import OrderedDict
import pymongo
from datetime import datetime as DateTime,timedelta as TimeDelta,time as Time
from dateutil.parser import parse
from dateutil.rrule import *
from functools import partial
from mantis.trade.types import ProductClass,TimeDuration
from vnpy.trader.vtObject import VtTickData,VtBarData
from mantis.trade.utils import get_symbol_prefix
from mantis.trade.trade_time import get_trade_timespace_by_product,\
    get_trade_timespace_by_exchange,is_trade_day,get_timespace_of_trade_day


CTP_TICK_DB = 'Ctp_Tick'
CTP_BAR_DB = 'Ctp_Bar_{}'

mongodb_conn = None
symbol_min_dict = OrderedDict() # { 'AP901':Set(DateTime(09,00),..) }

ts = list(rrule(MINUTELY,interval=1,dtstart=parse('2013-08-01 9:0'),until=parse('2013-08-01 10:45 ')))#间隔为3



def get_trade_timetable_template(symbol,productCls = ProductClass.Future):
    product = symbol
    if len(symbol) > 3:
        product = get_symbol_prefix(symbol)
    return get_trade_timespace_by_product(product)

def time_work_right_short(spaces,t):
    """
    考虑 开市前的1分钟集合竞价，每个交易尾端延时1分钟缓冲 '*'， 跨日'-'时段不考虑尾端延长

    """
    t = t.time()
    for space in spaces:

        if space[1] == Time(0,0) and t >=space[0]:
            return space
        e = (DateTime.combine(DateTime.now().date(), space[1]) + TimeDelta(minutes=1)).time()
        if t >= space[0] and t < e:  #  包含右侧结束时间(保持1分钟数据接收缓冲)
            return space
        if len(space) == 3 and space[-1].count('*'): # 时间段开始包括 1分钟的集合竞价时间
            s = (DateTime.combine( DateTime.now().date(),space[0]) - TimeDelta(minutes=1)).time()

            if t >= s  and t < e:
                return space
    return ()

# def time_work_right_close(spaces,t):
#     t = t.time()
#     for space in spaces:
#          if t >= space[0] and t <= space[1]:
#                 return True
#     return False

def get_day_trade_minute_line(product,date):
    """
    返回一天内指定合约交易时段内所有分钟计算点
    最后一分钟没有交易
    :param symbol:
    :param date: DateTime
    :return:
    """
    entries = get_trade_timetable_template(product)
    result = []
    for w in range(len(entries)):
        s,e = entries[w][:2]
        dts = DateTime(date.year,date.month,date.day,s.hour,s.minute,s.second)
        dte = DateTime(date.year,date.month,date.day,e.hour,e.minute,e.second) # - TimeDelta(minutes=1)
        if len(entries[w]) ==  3 and entries[w][-1].count('-'): # 跨天
            dts+=TimeDelta(days=1)
            dte+=TimeDelta(days=1)
        else:
            if dte < dts: # 跨天的行情
                dte = dte + TimeDelta(days=1)
        dte-=TimeDelta(minutes=1) # 不包括收尾分钟
        mins = list(rrule(MINUTELY, interval=1, dtstart=dts, until=dte))
        result+=mins
    return result


def get_day_trade_nminute_line(product,nmin,date):
    """
    返回一天内指定合约交易时段内指定n分钟间隔的时间计算点
    最后一分钟没有交易
    nmin - 3m 5m 15m 30m 60m
    """
    result = []
    if nmin not in (3,5,15,30,60):
        return result

    entries = get_trade_timetable_template(product)

    for w in range(len(entries)):
        s, e = entries[w][:2]
        smin = emin = 0
        if s.minute:
            smin = s.minute/nmin*nmin
        if e.minute:
            emin = e.minute/nmin*nmin
        dts = DateTime(date.year,date.month,date.day,s.hour,s.minute,s.second)
        dte = DateTime(date.year,date.month,date.day,e.hour,e.minute,e.second) #- TimeDelta(minutes=1)
        if len(entries[w]) ==  3 and entries[w][-1].count('-'): # 跨天
            dts+=TimeDelta(days=1)
            dte+=TimeDelta(days=1)
        else:
            if dte < dts: # 跨天的行情
                dte = dte + TimeDelta(days=1)

        dts = dts.replace(minute=smin,second=0,microsecond=0)
        dte = dte.replace(minute=emin,second=0,microsecond=0)
        if nmin!=60:
            dte -= TimeDelta(minutes=1)
        mins = list(rrule(MINUTELY, interval=nmin, dtstart=dts, until=dte))  # 间隔为3

        for min in mins:
            if result.count(min) == 0:
                result.append(min)
        # result+=mins
    return result

# def get_day_untrade_timerange(symbol,date):
#     """
#     返回一天内指定合约非交易时段内, 存在跨日时间
#     :param symbol:
#     :param date: DateTime
#     :return:
#     """
#     entries = get_trade_timetable_template(symbol)
#     result = []
#     zero = Time(0,0)
#     first = entries[0]
#     if zero != first[0]:
#         result.append( [zero,first[0]] )
#
#     gaps =[]
#     def _collect(result, x, y):
#         result.append([x[1],y[0]])
#         return y
#
#     reduce(partial(_collect, gaps), entries)
#     result+=gaps
#     last = entries[-1]
#     # if zero<= last[1]:
#     if zero == last[1] or last[1] >= last[0]: # 在一天之内
#         result.append( [last[1],zero] )
#     else: # 最后一项跨天了，忽略
#         pass
#
#
#     result = map(lambda _:
#                  [DateTime(date.year,date.month,date.day,_[0].hour,_[0].minute),
#                   DateTime(date.year, date.month, date.day, _[1].hour, _[1].minute)],
#                  result)
#     return result

# filter(partial(time_work,space_templetes['FUTURES_1']),ts)
#
# def is_trade_time(symbol,t,product = ProductClass.Future):
#     space = get_trade_timetable_template(symbol)
#     return time_work_right_open(space,t)
#
# def kline_make_prev_min_futures(symbol,t):
#     """
#     倒推一分钟开始计算分钟kline
#     :param symbol:
#     :param t:
#     :return:
#     """
#     # space = get_trade_timetable_template(symbol)
#     t = t - TimeDelta(minutes=1)
#     if not is_trade_time(symbol,t):
#         return
#
#     kline_make_min_futures(symbol,t)

def make_min_bar(symbol,t,nmin='1m',leftMargin=0,rightMargin=0,drop =True,product=ProductClass.Future):
    """
    开始计算指定开始分钟的 bar
    :drop  是否删除存在的分钟 bar

    1. 指定的分钟内没有tick数据
        取前一根有效的bar
        如果前无bar，则忽略本次bar计算

    """

    if nmin not in TimeDuration.SCALES.keys():
        print 'Error: paramter nmin:{} invalid.'.format(nmin)
        return
    mins = TimeDuration.SCALES[nmin]/TimeDuration.MINUTE
    t1 = t.replace(second=0,microsecond=0)
    t2 = t1 + TimeDelta(minutes=mins)
    conn = mongodb_conn
    dbname = CTP_TICK_DB
    coll = conn[dbname][symbol]

    p1 = t1 - TimeDelta(minutes=leftMargin)
    p2 = t2 + TimeDelta(minutes=rightMargin)

    rs = coll.find({'datetime':{'$gte':p1,'$lt':p2},'flag':0}).sort( (['datetime',pymongo.ASCENDING],['seq',pymongo.ASCENDING]))
    print symbol, p1, '-->', p2, ' count:',rs.count()
    dbname = CTP_BAR_DB
    collbar_1m = conn[dbname.format(nmin)][symbol]
    bar = None


    # 删除已存在 1m bar
    if drop:
        collbar_1m.remove({'datetime':t1})

    if rs.count() == 0: # 分钟内无tick数据 ，将连续之前的bar
        # if not prev_bar: #查找前一个bar
        prev_bar = None
        r = collbar_1m.find({'datetime':{'$lt':t1},'flag':0}).sort('datetime',pymongo.DESCENDING).limit(1)
        if r.count() :
            prev_bar = VtBarData()
            prev_bar.__dict__ = r[0]

        if prev_bar:
            prev_bar.datetime = t1
            prev_bar.date = prev_bar.datetime.strftime('%Y%m%d')
            prev_bar.time = prev_bar.datetime.strftime('%H:%M:%S.%f')
            prev_bar.high = prev_bar.close
            prev_bar.low = prev_bar.close
            prev_bar.open = prev_bar.close
            prev_bar.volume = 0
            bar = prev_bar
    else: # 计算当前分钟内的bar
        bar = VtBarData()
        tick = VtTickData()
        tick.__dict__ = rs[0]
        bar.datetime = t1
        bar.date = bar.datetime.strftime('%Y%m%d')
        bar.time = bar.datetime.strftime('%H:%M:%S.%f')
        bar.vtSymbol = tick.vtSymbol
        bar.symbol = tick.symbol
        bar.exchange = tick.exchange
        bar.open = tick.lastPrice
        bar.high = tick.lastPrice
        bar.low = tick.lastPrice
        last = None
        #找到前一个k线最后一个tick作为last
        rs = coll.find({'datetime': {'$lt': p1}, 'flag': 0}).sort((['datetime', pymongo.DESCENDING], ['seq', pymongo.DESCENDING])).limit(1)
        if rs.count():
            last = VtTickData()
            last.__dict__ = rs[0]
        # --
        for r in rs:
            tick = VtTickData()
            tick.__dict__ = r
            bar.high = max(bar.high, tick.lastPrice)
            bar.low = min(bar.low, tick.lastPrice)

            bar.close = tick.lastPrice
            bar.openInterest = tick.openInterest
            if last:
                bar.volume += (tick.volume - last.volume)
            last = tick
    if bar: #写入bar
        dict_ = bar.__dict__
        if dict_.has_key('_id'):
            del dict_['_id']
        collbar_1m.insert_one(dict_)
        print 'Write {} Bar:'.format(nmin),bar.__dict__
    return bar

def make_day_bar(symbol,date,drop =True,product=ProductClass.Future):
    """
    计算日线
    """
    from logging import getLogger
    if isinstance(date,str):
        date = parse(date)
    date = date.replace(hour=0,minute=0,second=0,microsecond=0)
    days = get_timespace_of_trade_day(date)
    bar = None
    if not days:
        getLogger().info("day span is None")
        return None
    t1,t2 = days

    conn = mongodb_conn
    dbname = CTP_TICK_DB
    coll = conn[dbname][symbol]

    rs = coll.find({'datetime':{'$gte':t1,'$lte':t2},'flag':0}).sort( (['datetime',pymongo.ASCENDING],['seq',pymongo.ASCENDING]))
    print symbol, t1, '-->', t2, ' count:',rs.count()
    dbname = CTP_BAR_DB
    collbar_1m = conn[dbname.format('1d')][symbol]

    # 删除已存在 1m bar
    if drop:
        collbar_1m.remove({'datetime':date})
    # 注意，记录的日期是日盘交易的日期
    if rs.count() == 0: # 分钟内无tick数据 ，将连续之前的bar
        # if not prev_bar: #查找前一个bar
        prev_bar = None
        r = collbar_1m.find({'datetime':{'$lt':t1},'flag':0}).sort('datetime',pymongo.DESCENDING).limit(1)
        if r.count() :
            prev_bar = VtBarData()
            prev_bar.__dict__ = r[0]

        if prev_bar:
            prev_bar.datetime = date
            prev_bar.date = prev_bar.datetime.strftime('%Y%m%d')
            prev_bar.time = prev_bar.datetime.strftime('%H:%M:%S.%f')
            prev_bar.high = prev_bar.close
            prev_bar.low = prev_bar.close
            prev_bar.open = prev_bar.close
            prev_bar.volume = 0
            bar = prev_bar
    else: # 计算当前分钟内的bar
        bar = VtBarData()
        tick = VtTickData()
        tick.__dict__ = rs[0]
        bar.datetime = date
        bar.date = bar.datetime.strftime('%Y%m%d')
        bar.time = bar.datetime.strftime('%H:%M:%S.%f')
        bar.vtSymbol = tick.vtSymbol
        bar.symbol = tick.symbol
        bar.exchange = tick.exchange
        bar.open = tick.lastPrice
        bar.high = tick.lastPrice
        bar.low = tick.lastPrice
        last = None

        # 找到前一个k线最后一个tick作为last
        rs = coll.find({'datetime': {'$lt': t1}, 'flag': 0}).sort(
            (['datetime', pymongo.DESCENDING], ['seq', pymongo.DESCENDING])).limit(1)
        if rs.count():
            last = VtTickData()
            last.__dict__ = rs[0]

        for r in rs:
            tick = VtTickData()
            tick.__dict__ = r
            bar.high = max(bar.high, tick.lastPrice)
            bar.low = min(bar.low, tick.lastPrice)

            bar.close = tick.lastPrice
            bar.openInterest = tick.openInterest
            if last:
                bar.volume += (tick.volume - last.volume)
            last = tick
    if bar: #写入bar
        dict_ = bar.__dict__
        if dict_.has_key('_id'):
            del dict_['_id']
        collbar_1m.insert_one(dict_)
        print 'Write {} Bar:'.format(str(date.date())),bar.__dict__
    return bar


min_bar_made_history={}

def get_minbar_key(symbol,scale,time):
    time = time.replace(second=0,microsecond=0)
    key = '{}.{}.{}'.format(symbol,scale,str(time))
    return key

def make_lastest_min_bar(symbol,test_time=None):
    """计算最近的1分钟 bar"""
    t = DateTime.now()
    if test_time:
        t = test_time
    t = t - TimeDelta(minutes=1) # 前一分钟
    key = get_minbar_key(symbol,'1m',t)
    if min_bar_made_history.has_key(key):
        return None
    min_bar_made_history[key] = 1

    spaces = get_trade_timetable_template(symbol)
    bar = None
    if time_work_right_short(spaces,t):
        bar = make_min_bar(symbol,t,drop=True)
    return bar

def make_latest_nmin_bar(symbol,scale,test_time=None):
    """
    计算多分钟的bar

    """
    if scale not in TimeDuration.SCALES.keys():
        return None
    now = DateTime.now()
    if test_time:
        now = test_time
    nmin = TimeDuration.SCALES[scale] / TimeDuration.MINUTE
    # t = DateTime.now()
    # t = t - TimeDelta(minutes=1)  # 前一分钟


    t = now - TimeDelta(minutes=nmin)
    min = t.minute/nmin*nmin
    t = t.replace(minute=min,second=0,microsecond=0)

    spaces = get_trade_timetable_template(symbol)
    bar = None
    space = time_work_right_short(spaces, t)
    if space:
        key = get_minbar_key(symbol, scale, t)
        if min_bar_made_history.has_key(key):
            return  None
        min_bar_made_history[key] = 1
        print str(t)
        left = 0
        right = 1
        if len(space) == 3 and space[-1].count('*'): # 开盘集合竞价
            left = 1
        if len(space) == 3 and space[-1].count('-'): # 跨日时间
            right = 0
        bar = make_min_bar(symbol, t, scale,drop=True,leftMargin=left,rightMargin=right)
    return bar

def data_clear_days(symbol,start,end='',readonly=False):
    """
    删除指定时间范围内非交易时间段的tick数据
    """
    import logging
    logger = logging.getLogger()

    if isinstance(start,str):
        start = parse(start)
    if not end:
        end = start
    else:
        end = parse(end)
    end = end + TimeDelta(days=1)

    conn = mongodb_conn
    coll = conn[CTP_TICK_DB][symbol]

    spaces = get_trade_timetable_template(symbol)
    # print spaces
    f = open('data_clear_{}.txt'.format(str(start.date())),'w')

    if readonly:
        rs = coll.find({'datetime': {'$gte':start,'$lt':end}})
    else:
        rs = coll.find({'datetime': {'$gte':start,'$lt':end},'flag':0})
    for r in rs:
        if not time_work_right_short(spaces,r['datetime']):
            # coll.delete_one({'_id':r['_id']})
            if not readonly:
                coll.update_one(filter={'_id':r['_id']},update={'$set':{'flag':1}})
            # print 'Removed Record:',str(r['datetime'])
            logger.debug( 'Removed Record:'+ r['symbol'] +' '+ str(r['datetime']) )
            f.write("{} {} {}\n".format(r['symbol'],str(r['datetime']),str(r)))
    f.close()



if __name__ == '__main__':
    f = open('test.txt','w')
    mins =  get_day_trade_minute_line('m1901',parse('2018-8-15'))
    ss = '\n'.join(map(str,mins))
    f.write(ss)
    f.close()
    # print mins
    print get_day_trade_nminute_line('m1901',5,parse('2018-8-15'))

    # data_clear_days('AP901','2018-7-27')