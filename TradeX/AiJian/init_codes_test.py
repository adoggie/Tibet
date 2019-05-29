#coding:utf-8
"""
初始化策略运行控制参数
"""
import  sys
import copy
import datetime
from dateutil.parser import parse
from mantis.sg.fisher import model as model

"""
定义所有证券代码信息
"""
CODES={
    '600834': u'申通地鐵' ,
        '600776': u'东方通信' ,
       '600682':  u'南京新百',
        '600460': u'士兰微',
       }

CODES_TRADING = {
    '600736': u'苏州高新',
        '600064': u'南京高科',
        '600575': u'皖江物流',
        '601878':  u'浙商证券',
       '600650':  u'锦江投资',
       '300252': u'金信诺' ,
       '300310': u'宜通世纪' ,
        '002517':u'愷英網絡',
        '601258': u'庞大集团',
        '002835': u'同为股份',
        '002367': u'康力电梯',
        '300590': u'移为通信',
        '603118': u'共进股份',
        '002235': u'安妮股份',
        '600298': u'安琪酵母',
        '000823': u'超声电子',
        '600816': u'安信信托',
        '300461': u'田中精机',
        '002226': u'江南化工'
}

CODES.update( CODES_TRADING)

CODES_INIT_POS = copy.deepcopy(CODES_TRADING)   # 初始化持仓的票

# 所有运行策略定义列表
strategies = [
    # dict( strategy_id= 'TDX_Test1', conn_url='dongfang'),


    dict( strategy_id= 'TEST', conn_url='aijian' ,
          # codes = ('002517','600064','300310') ,
          # codes = CODES_TRADING.keys() ,
          code_params = None,
          codes = {
            '600736':dict(buy_diff_rate=-0.02, sell_diff_rate=0.02, buy_qty= 100, sell_qty=100, limit_buy_qty=400,limit_sell_qty=400),
            '600064':dict(buy_diff_rate=-0.02, sell_diff_rate=0.02, buy_qty= 100, sell_qty=100, limit_buy_qty=400,limit_sell_qty=400),
            '600575':dict(buy_diff_rate=-0.02, sell_diff_rate=0.02, buy_qty= 100, sell_qty=100, limit_buy_qty=400,limit_sell_qty=400),
            '601878':dict(buy_diff_rate=-0.02, sell_diff_rate=0.02, buy_qty= 100, sell_qty=100, limit_buy_qty=400,limit_sell_qty=400),
            '600650':dict(buy_diff_rate=-0.02, sell_diff_rate=0.02, buy_qty= 100, sell_qty=100, limit_buy_qty=400,limit_sell_qty=400),
            '300252':dict(buy_diff_rate=-0.02, sell_diff_rate=0.02, buy_qty= 100, sell_qty=100, limit_buy_qty=400,limit_sell_qty=400),
            '300310':dict(buy_diff_rate=-0.02, sell_diff_rate=0.02, buy_qty= 100, sell_qty=100, limit_buy_qty=400,limit_sell_qty=400),
            '002517':dict(buy_diff_rate=-0.02, sell_diff_rate=0.02, buy_qty= 100, sell_qty=100, limit_buy_qty=400,limit_sell_qty=400),
            '601258':dict(buy_diff_rate=-0.02, sell_diff_rate=0.02, buy_qty= 100, sell_qty=100, limit_buy_qty=400,limit_sell_qty=400),
            '002835':dict(buy_diff_rate=-0.02, sell_diff_rate=0.02, buy_qty= 100, sell_qty=100, limit_buy_qty=400,limit_sell_qty=400),
            '002367':dict(buy_diff_rate=-0.02, sell_diff_rate=0.02, buy_qty= 100, sell_qty=100, limit_buy_qty=400,limit_sell_qty=400),
            '300590':dict(buy_diff_rate=-0.02, sell_diff_rate=0.02, buy_qty= 100, sell_qty=100, limit_buy_qty=400,limit_sell_qty=400),
            '603118':dict(buy_diff_rate=-0.02, sell_diff_rate=0.02, buy_qty= 100, sell_qty=100, limit_buy_qty=400,limit_sell_qty=400),
            '002235':dict(buy_diff_rate=-0.02, sell_diff_rate=0.02, buy_qty= 100, sell_qty=100, limit_buy_qty=400,limit_sell_qty=400),
            '600298':dict(buy_diff_rate=-0.02, sell_diff_rate=0.02, buy_qty= 100, sell_qty=100, limit_buy_qty=400,limit_sell_qty=400),
            '000823':dict(buy_diff_rate=-0.02, sell_diff_rate=0.02, buy_qty= 100, sell_qty=100, limit_buy_qty=400,limit_sell_qty=400),
            '600816':dict(buy_diff_rate=-0.02, sell_diff_rate=0.02, buy_qty= 100, sell_qty=100, limit_buy_qty=400,limit_sell_qty=400),
            '300461':dict(buy_diff_rate=-0.02, sell_diff_rate=0.02, buy_qty= 100, sell_qty=100, limit_buy_qty=400,limit_sell_qty=400),
            '002226':dict(buy_diff_rate=-0.02, sell_diff_rate=0.02, buy_qty= 100, sell_qty=100, limit_buy_qty=400,limit_sell_qty=400),
                      },
          enable = 1,
          run = 1,
          comment = u'运行日内振幅策略',
          customized = True , # 自定义每一个股票参数设置
          ), # 爱建

]


def init_mongodb(host='127.0.0.1',port=27017,date = None):
    """
    date : str 默认为当日
    """
    from pymongo import MongoClient
    from mantis.sg.fisher.stutils import get_trade_database_name

    dbname = get_trade_database_name(date = date)

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
        code_params = _.get('code_params')

        del _['codes']
        del _['code_params']

        sp = model.StrategyParam()
        sp.assign(_)
        sp.save()

        if isinstance(codes,(list,tuple)):
            for code in codes:
                cs = model.CodeSettings.get(code = code , strategy_id = _['strategy_id'])
                if not cs:
                    cs = model.CodeSettings()
                    cs.code = code
                    cs.name = CODES[code]
                    cs.strategy_id = _['strategy_id']
                    cs.assign( code_params ).save()
        if isinstance(codes,dict):
            for code,params in codes.items():
                cs = model.CodeSettings.get(code=code, strategy_id=_['strategy_id'])
                if not cs:
                    cs = model.CodeSettings()
                    cs.code = code
                    cs.name = CODES[code]
                    cs.strategy_id = _['strategy_id']
                    cs.assign(params).save()

# 生成当天数据库的策略配置参数
if __name__ == '__main__':
    date = None
    sys.argv.append('20200520')
    if len(sys.argv) > 1:
        date = sys.argv[-1]
    db = init_mongodb(host='192.168.1.252', date=date)

    init_all(db)
    print 'Strategy Configuration Finished!'
    # print model.ConnectionUrl.get()


