#coding:utf-8
"""
初始化 交易账号 TradeX
"""
import sys
from mantis.sg.fisher import model as model


connection_urls = [
    dict(
        id = 'ctp-simnow',name = u'simnow',
        md_broker="192.168.1.252:6379:0:",
        td_api_url = 'http://192.168.1.252:17001' ,
        td_stream = '192.168.1.252:7700'

        )
]


def init_mongodb(host='127.0.0.1',port=27017,date = None):
    """
    date : str 默认为当日
    """
    from pymongo import MongoClient
    from mantis.sg.fisher.stutils import get_trade_database_name

    # dbname = get_trade_database_name(date = date)
    dbname ='TradeFisherCtp'
    mg_conn = MongoClient(host, port)
    model.set_database(mg_conn[dbname])
    return mg_conn

def init_all(db):
    model.ConnectionUrl.collection().remove()
    for _ in connection_urls:
        url = model.ConnectionUrl()
        url.assign(_).save()

# 支持初始化指定的日期数据库
if __name__ == '__main__':
    date = None
    if len(sys.argv) > 1:
        date = sys.argv[-1]
    db = init_mongodb(host='192.168.1.252' , date = date )
    init_all(db)
    print model.ConnectionUrl.get()


