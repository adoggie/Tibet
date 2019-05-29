# coding:utf-8

import json
import datetime
from mantis.fundamental.application.app import instance
from vnpy.trader.vtObject import VtTickData

def get_symbol_ticks(message,ctx):
    """订阅的所有合约行情数据"""
    topic = ctx.get('name')
    data = message
    # topic: 订阅的通道名称 ctp_ticks_*
    symbol = topic.split('_')[-1]

    tick = json.loads(data)
    tick['datetime'] = datetime.datetime.strptime(' '.join([tick.get('date'), tick.get('time')]), '%Y%m%d %H:%M:%S.%f')
    tickobj = VtTickData()
    tickobj.__dict__ = tick

    main = instance.serviceManager.get('main')
    # debug = main.cfgs.get('debug',{})
    # if debug.get('enable',False) and symbol in debug.get('symbols',[]):
    #     main.onTick(symbol,tickobj)
    # else:
    main.onTick(symbol,tickobj)

    """
    貌似凭借多年经验感觉错误在于 redis的接收线程读取数据之后，处理数据，并再将数据发送回redis，期间在一个线程中执行导致的故障 
    所以应该将接收的数据置入 Queue，处理程序从Queue中获取数据处理，并将数据发送回去 
    
    gevent能运行，但出现了故障，一个条件被重入了，所以肯定是这个问题
    """
