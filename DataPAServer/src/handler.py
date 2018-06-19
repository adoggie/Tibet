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
    main.onTick(symbol,tickobj)
