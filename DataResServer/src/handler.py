# coding:utf-8

import json
import datetime
from mantis.fundamental.application.app import instance

CTP_TICK_DB_NAME ='Ctp_Tick'
CTP_BAR_DB_NAME = 'Ctp_Bar'


def get_message_on_ctp_ticks(data,ctx):
    """get message from market-adapter via redis-queue, then put it into mongodb"""
    tick = json.loads(data)
    tick['datetime'] = datetime.datetime.strptime(' '.join([tick.get('date'), tick.get('time')]), '%Y%m%d %H:%M:%S.%f')
    tablename = tick.get('_table_')
    if not tablename:
        tablename = tick.get('vtSymbol')
    conn = instance.datasourceManager.get('mongodb').conn
    db = conn[CTP_TICK_DB_NAME]
    table = db[tablename]
    table.insert_one(tick)


def get_message_on_ctp_bars(data,chan):
    # chan.props.get('bar')
    tablename = data.get('_table_')
    conn = instance.datasourceManager.get('mongodb')
    db = conn[CTP_BAR_DB_NAME]
    table = db[tablename]
    table.insert_one(data)