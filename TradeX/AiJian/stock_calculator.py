#coding:utf-8

"""
股票交易成本计算
"""

"""
#### 1. 买入
- 佣金 : 5 
- 印花税:0 
- 过户费： 深市 0 ,   沪 0.03% 
- 其他 : 0 

#### 2. 卖出
- 佣金 : 5 
- 印花税: 0.1% 
- 过户费： 深市 0  沪 0.03% 
- 其他 : 0 

"""
Market_SH = 1
Market_SZ = 0
Market_NULL = 99
def getMaketTypeByCode(code):
    if not code:
        return Market_NULL
    if code[0] in ('0','3'):
        return Market_SZ
    return Market_SH

FIXED_COMMISSION = 5 # 固定佣金

def getStampTaxRatio(direction,market):
    ratio = 0
    if direction == 'short':
        ratio = 0.001
    return  ratio

def getTransferFeeRatio(direction,market):
    ratio = 0
    if direction == 'long':
        if market == Market_SH:
            ratio = 0.0003
    if direction == 'short':
        if market == Market_SH:
            ratio = 0.0003
    return  ratio

def getOtherFeeRatio(direction,market):
    return 0

def calc(code,long_price,short_price,num):
    """

    :param code:  股票代码
    :param long_price: 买入价格
    :param short_price: 卖出价格
    :param num: 数量
    :return:
    """
    market = getMaketTypeByCode(code)

    #- 计算买入
    ratio = getStampTaxRatio('long',market)
    long_amount = long_price * num
    long_cost = 0
    if ratio:
        long_cost += ratio *long_amount
    ratio = getTransferFeeRatio('long',market)
    if ratio:
        long_cost += long_amount * ratio
    long_cost += FIXED_COMMISSION

    # - 计算卖出
    ratio = getStampTaxRatio('short', market)
    short_amount = short_price * num
    short_cost = 0
    if ratio:
        short_cost += ratio * short_amount
    ratio = getTransferFeeRatio('short', market)
    if ratio:
        short_cost += short_amount * ratio
    short_cost += FIXED_COMMISSION

    print ''
    diff = (short_price-long_price) / (long_price*1.0) *100
    print 'long:',long_price ,' short：',short_price , 'diff: {}%'.format(diff),  ' num:',num
    print u'amount/long:',long_amount
    print u'amount/short:',short_amount
    print u'cost total:', long_cost +  short_cost , '(long:' , long_cost, 'short:',short_cost ,')'
    print u'profit total:' , short_amount - long_amount - (long_cost +  short_cost )
    print '-'*30
    # return  (long_amount , short_amount , short_amount - long_amount, long_cost , short_cost , )

price = 8
diff_ratio = 0.02

for num in [2,]:
    for p in range(3,12):
        calc('6553333', p , p*(1 + diff_ratio),num*100)
