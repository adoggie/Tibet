# coding:utf-8

import json
import datetime
from mantis.fundamental.application.app import instance
from mantis.fundamental.utils.timeutils import datetime_to_timestamp
from mantis.fundamental.utils.useful import Sequence

CTP_TICK_DB_NAME ='Ctp_Tick'
CTP_BAR_DB_NAME = 'Ctp_Bar'

sequence = Sequence()

def get_message_on_ctp_ticks(message,ctx):
    data = message
    tick = json.loads(data)
    dt = datetime.datetime.fromtimestamp(tick['Timestamp'])
    tick['DateTime'] = dt
    tick['SaveTime'] = datetime.datetime.now()

    tablename = tick.get('InstrumentID')
    conn = instance.datasourceManager.get('mongodb').conn
    # 数据库名称可以配置在 settings.yaml 的 messagebroker 栏目 的channel.extra属性中
    dbname = ctx.get('channel').cfgs.get('extra',{}).get('db_name',CTP_TICK_DB_NAME)
    db = conn[dbname]
    table = db[tablename]
    table.insert_one(tick)

def get_message_on_ctp_bars(message,ctx):
    # chan.props.get('bar')

    bar = json.loads(message)
    bar['datetime'] = datetime.datetime.strptime(' '.join([bar.get('date'), bar.get('time')]), '%Y%m%d %H:%M:%S.%f')
    bar['ts'] = datetime_to_timestamp(bar['datetime'])
    tablename = bar.get('_table_')
    if not tablename:
        tablename = bar.get('vtSymbol')
    conn = instance.datasourceManager.get('mongodb').conn
    scale = bar.get('scale','')
    dbname = ctx.get('channel').cfgs.get('extra', {}).get('db_name', CTP_BAR_DB_NAME)
    dbname = dbname.format(scale=scale)
    db = conn[dbname]
    table = db[tablename]
    table.insert_one(bar)