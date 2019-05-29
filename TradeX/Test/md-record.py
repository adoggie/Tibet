#coding:utf-8

import json
from utils.useful import hash_object
from utils.timeutils import current_datetime_string
import pandas
import numpy
import talib
# import tushare

STOCK_LIST = ['000001']

bar_log_file ='bar.log'
tick_log_file ='tick.log'

def print_line(text,fp=None):
    text = str(text)
    if fp:
        fp.write (current_datetime_string())
        fp.write(text+'\n')
        fp.flush()
    print text

def initialize(context):
    context.add_md(source=SOURCE.XTP)
    context.add_td(source=SOURCE.XTP)
    context.subscribe(tickers=STOCK_LIST, source=SOURCE.XTP)
    context.register_bar(source=SOURCE.XTP, min_interval=1, start_time='09:30:00', end_time='15:00:00')
    context.register_bar(source=SOURCE.XTP, min_interval=5, start_time='09:30:00',  end_time='15:00:00')
    context.register_bar(source=SOURCE.XTP, min_interval=15, start_time='09:30:00',  end_time='15:00:00')
    context.register_bar(source=SOURCE.XTP, min_interval=30, start_time='09:30:00',  end_time='15:00:00')
    context.register_bar(source=SOURCE.XTP, min_interval=60, start_time='09:30:00',  end_time='15:00:00')
    context.trade = True
    context.barlog = open(bar_log_file,'a+')
    context.ticklog = open(tick_log_file,'a+')

def on_pos(context, pos_handler, request_id, source, rcv_time):
    if(request_id == -1) and(pos_handler is None):
        context.set_pos(context.new_pos(SOURCE.XTP), SOURCE.XTP)
    else:
        context.log_info("[RSP_POS] {}".format(pos_handler.dump()))


def save_bar_data(code,bar,interval):
    # 非交易时间段丢弃
    f = open('{}-{}.txt'.format(code,interval),'a+')
    data = json.dumps(hash_object(bar))
    f.write(data+'\n')
    f.close()

def on_bar(context, bars, intervals,source, rcv_time):

    print_line( ' bars info  '.center(40, '=') ,context.barlog)
    print_line('>>on_bar()' + str(bars) + ' intervals:{} source:{} {}'.format(intervals, source, rcv_time),
               context.barlog)

    for code,bar in bars.items():
        print_line( code + ' '+ str(hash_object(bar)) ,context.barlog)
        save_bar_data(code,bar,intervals)

def on_error(context, error_id, error_msg, order_id, source, rcv_time):
    context.log_error("[ERROR] (err_id){} (err_msg){} (order_id){} (source){}".format(error_id, error_msg, order_id, source))


def on_tick(context, md, source, rcv_time):
    # return
    print '>>on_tick()' , md,source,rcv_time
    print_line( ' md info (Ticks) '.center(40,'=') ,context.ticklog)
    print_line( hash_object(md) ,context.ticklog)
    if context.trade:
        last_price = md.LastPrice

        # rid = context.insert_limit_order(source=SOURCE.XTP,
        #                                  ticker=md.InstrumentID,
        #                                  exchange_id=EXCHANGE.SZE,
        #                                  price=last_price,
        #                                  volume=100,
        #                                  direction=DIRECTION.Buy,
        #                                  offset=OFFSET.Open)
        context.trade = False
    else:
        print 'to stop()..'
        # context.stop()

def on_rtn_order(context, rtn_order, order_id, source, rcv_time):
    context.log_info("on_rtn_order|order_id:{}|stock:{}|trade:{}|left:{}|status:{}".format(order_id, rtn_order.InstrumentID, rtn_order.VolumeTraded, rtn_order.VolumeTotal, rtn_order.OrderStatus))


def on_rtn_trade(context, rtn_trade, order_id, source, rcv_time):
    context.log_info("on_rtn_trade|order_id:{}|stock:{}|price:{}|volume:{}".format(order_id,rtn_trade.InstrumentID,rtn_trade.Price,rtn_trade.Volume))
