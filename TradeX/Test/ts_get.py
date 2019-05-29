#coding:utf-8

from functools import partial
import tushare as ts


"""
tushare.pro版本开源版本不提供除了日线之外的k线， 中泰流程开通可以提供
tushare老版本 可查询除了昨日之外的历史分钟线
    ts.get_hist_data('000001',start='2019-01-09',end='2019-01-09',ktype='5')


"""
api_token = 'da60f22fd6344c9392357ec174b961c1dbf35f2a49a5f8f9a65748c0'
# ts.set_token(api_token)

api = None

def get_ts_api():
    global api
    if not api:
        api = ts.pro_api(api_token)
    return api

def ts_code_fix(code):
    if code[0] == '6':
        code += '.SH'
    else:
        code += '.SZ'
    return code

def pro_bar(*args,**kwargs):
    api = get_ts_api()
    kwargs['pro_api'] = api

    if kwargs.get('ts_code'):
        code =  kwargs.get('ts_code')
        code = ts_code_fix(code)
        kwargs['ts_code'] = code
        # print code
    # print kwargs
    return ts.pro_bar(*args,**kwargs)

def get_hist_data(*args,**kwargs):
    return ts.get_hist_data(*args,**kwargs)



def daily(*args,**kwargs):
    api = get_ts_api()
    if kwargs.get('ts_code'):
        code =  kwargs.get('ts_code')
        code = ts_code_fix(code)
        kwargs['ts_code'] = code

    return api.daily(*args,**kwargs)

if __name__ == '__main__':
    import datetime
    # print get_ts_api().daily(ts_code='000001.SZ',trade_date='20190104')
    # print pro_bar(ts_code='000001.SZ',trade_date='20190104')
    # api = get_ts_api()
    # ts.set_token(api_token)
    # api = ts.pro_api(api_token)
    # print api.daily(ts_code='000001.SZ',trade_date='20190104')
    # print ts.pro_api(api_token)

    # print ts.pro_bar(pro_api=api,ts_code='000001.SZ')
    # print pro_bar(pro_api=api,ts_code='000001.SZ')
    print pro_bar(ts_code='000001',freq='5',start_date='20190109',end_date='20190109') #.head(2)
    
    # print daily(ts_code='000001',trade_date='20190109').iloc[0]['close']

    # start = datetime.datetime.now() - datetime.timedelta(days=20)
    # start = start.strftime('%Y%m%d')
    # end = datetime.datetime.now()
    # end = end.strftime('%Y%m%d')
    # print daily(ts_code='000001', start_date=start, end_date=end).iloc[0]['close']
