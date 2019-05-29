#coding:utf-8
"""
wingchun strategy -n s1 -p test_by.py

"""
import stbase
import simple_st

from utils.useful import hash_object



STOCK_LIST = simple_st.STOCK_LIST

bar_log_file ='bar.log'
tick_log_file ='tick.log'

stbase.TradeManager().init().addStock(STOCK_LIST)

def print_line(text,fp=None):
    text = str(text)
    # if fp:
    #     fp.write(text+'\n')
    #     fp.flush()
    print text

def on_timer(context):
    # print '>> onTimer()..'
    context.insert_func_after_c(1,on_timer)

def initialize(context):
    stbase.TradeManager().kf_proxy.on_init(context)
    stbase.TradeManager().any.trade = True
    print  '=='*30


def on_pos(context, pos_handler, request_id, source, rcv_time):
    # print 'on_pos..'
    # print pos_handler.dump()
    # print pos_handler.get_tickers()

    stbase.TradeManager().kf_proxy.on_pos(pos_handler, request_id, source, rcv_time)

def on_bar(context, bars, intervals,source, rcv_time):
    simple_st.strategy_exec_bar(bars, intervals, source, rcv_time)


def on_error(context, error_id, error_msg, order_id, source, rcv_time):
    context.log_error("[ERROR] (err_id){} (err_msg){} (order_id){} (source){}".format(error_id, error_msg, order_id, source))

import json
def get_available(context):
    pos_handler = context.get_pos(SOURCE.XTP)
    pnl_j = json.loads(pos_handler.dump())
    try:
        cash = pnl_j['Cash']['infos'][2]
    except:
        cash = 0
    return cash

def on_tick(context, md, source, rcv_time):
    stbase.TradeManager().kf_proxy.on_tick(md, source, rcv_time)

def on_rtn_order(context, rtn_order, order_id, source, rcv_time):
    print "=="*20
    context.log_info("on_rtn_order|order_id:{}|stock:{}|trade:{}|left:{}|status:{}".format(order_id, rtn_order.InstrumentID, rtn_order.VolumeTraded, rtn_order.VolumeTotal, rtn_order.OrderStatus))


def on_rtn_trade(context, rtn_trade, order_id, source, rcv_time):
    context.log_info("on_rtn_trade|order_id:{}|stock:{}|price:{}|volume:{}".format(order_id,rtn_trade.InstrumentID,rtn_trade.Price,rtn_trade.Volume))
