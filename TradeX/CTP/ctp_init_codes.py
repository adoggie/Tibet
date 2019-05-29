#coding:utf-8
"""
初始化策略运行控制参数
"""
import  sys
import copy
import traceback
import time
import datetime
from dateutil.parser import parse
import requests

from mantis.sg.fisher import model as model


td_api_url = 'http://192.168.1.252:17001'
mongodb_host = '192.168.1.252'
database_name = 'TradeFisherCtp'
"""
定义所有证券代码信息
"""
CODES={
        'm1909': u'm1909' ,
        'AP910': u'AP910' ,
       }

CODES_TRADING = {

}

CODES.update( CODES_TRADING)

CODES_INIT_POS = copy.deepcopy(CODES_TRADING)   # 初始化持仓的票

# 所有运行策略定义列表
strategies = [

    dict(
        strategy_id= 'CTP_TRADE1',
        conn_url='ctp-simnow' ,
        codes={
              'm1909': dict(),
              'AP910': dict(),
        },
        enable = 1,run = 1,comment = u'运行日内振幅策略'
    ), #
]


def init_mongodb(host='127.0.0.1',port=27017,date = None):
    """
    date : str 默认为当日
    """
    from pymongo import MongoClient
    from mantis.sg.fisher.stutils import get_trade_database_name

    # dbname = get_trade_database_name(dbname = 'TradeFisherCtp',date = date)
    dbname = database_name
    mg_conn = MongoClient(host, port)
    model.set_database(mg_conn[dbname])
    return mg_conn


CODE_CLEARS = False

def init_all(db):
    model.StrategyParam.collection().remove()

    if CODE_CLEARS:
        model.CodeSettings.collection().remove()

    for _ in strategies:
        codes = _['codes']
        del _['codes']

        sp = model.StrategyParam()
        sp.assign(_)
        sp.save()


        for code,params in codes.items():
            cs = model.CodeSettings.get(code = code , strategy_id = _['strategy_id'])
            if not cs:
                cs = model.CodeSettings()
                cs.code = code
                cs.name = CODES[code]
                cs.strategy_id = _['strategy_id']
                cs.assign( params ).save()



def requestFreshInstrument(code):
    """请求trader 刷新合约信息"""
    print 'requestFreshInstrument() , code:',code
    url = td_api_url + '/ctp/instrument/query'
    data = {}
    try:
        params = dict(instrument=code)
        res = requests.post(url, params)
        data = res.json().get('result', {})
    except:
        traceback.print_exc()
    return data

def init_code_more_info():
    """初始化合约相关信息(手续费，保证金)"""
    for code in CODES.keys():
        requestFreshInstrument(code)
        time.sleep(1)

    time.sleep(3)
    for code in CODES.keys():
        url = td_api_url + '/ctp/instrument/detail'
        data = {}
        try:
            params = dict(instrument=code)
            res = requests.get(url, params)
            data = res.json().get('result', {})
            item = model.CodeBasicInfo.get(code= code)
            if item:
                item.delete()
            item = model.CodeCommissionRate.get(code=code)
            if item:
                item.delete()

            item = model.CodeMarginRate.get(code=code)
            if item:
                item.delete()

            item = model.CodeBasicInfo()
            item.code = code
            item.name = data['instrument']['InstrumentName']
            item.assign(data['instrument'])
            item.save()

            item = model.CodeCommissionRate()
            item.code = code
            item.name = code
            item.assign(data['commission_rate'])
            item.save()

            item = model.CodeMarginRate()
            item.code = code
            item.name = code
            item.assign(data['margin_rate'])
            item.save()

        except:
            traceback.print_exc()



# 生成当天数据库的策略配置参数
if __name__ == '__main__':
    date = None
    if len(sys.argv) > 1:
        date = sys.argv[-1]
    db = init_mongodb(host= mongodb_host, date=date)

    # init_all(db)

    init_code_more_info()

    print 'Strategy Configuration Finished!'
    # print model.ConnectionUrl.get()


