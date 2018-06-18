# coding:utf-8

import json
import datetime
from mantis.fundamental.application.app import instance

CTP_TICK_DB_NAME ='Ctp_Tick'
CTP_BAR_DB_NAME = 'Ctp_Bar'


def get_message_on_ctp_ticks(message,ctx):
    """get message from market-adapter via redis-queue, then put it into mongodb
    message 从redis的list获取(blpop) message就是发送数据
    """
    data = message
    tick = json.loads(data)
    tick['datetime'] = datetime.datetime.strptime(' '.join([tick.get('date'), tick.get('time')]), '%Y%m%d %H:%M:%S.%f')
    tablename = tick.get('_table_')
    if not tablename:
        tablename = tick.get('vtSymbol')
    conn = instance.datasourceManager.get('mongodb').conn
    # 数据库名称可以配置在 settings.yaml 的 messagebroker 栏目 的channel.extra属性中
    dbname = ctx.get('channel').cfgs.get('extras',{}).get('db_name',CTP_TICK_DB_NAME)
    db = conn[dbname]
    table = db[tablename]
    table.insert_one(tick)


def get_message_on_ctp_bars(message,ctx):
    # chan.props.get('bar')
    bar = json.loads(message)
    bar['datetime'] = datetime.datetime.strptime(' '.join([bar.get('date'), bar.get('time')]), '%Y%m%d %H:%M:%S.%f')
    tablename = bar.get('_table_')
    conn = instance.datasourceManager.get('mongodb')
    scale = bar.get('scale','')
    dbname = ctx.get('channel').cfgs.get('extras', {}).get('db_name', CTP_BAR_DB_NAME)
    dbname = dbname.format(scale=scale)
    db = conn[dbname]
    table = db[tablename]
    table.insert_one(bar)