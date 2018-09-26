#coding:utf-8


# https://python-binance.readthedocs.io/en/latest/
# https://github.com/sammchardy/python-binance/blob/master/docs/websockets.rst

import time
api_key = 'a89RHztsZkykoOTazLHjM9HkZHML6j8UND0fUMaa1Thk731r9FgKjcttVlhWhuRh'
api_secret = 'OYxgsFpxeefBzFUmU4UDRLcFc790CCscFgWEU8pFSOFbHkvP4JSHUWBKMtQfPyC8'

from binance.client import Client
client = Client(api_key, api_secret)

# get market depth
depth = client.get_order_book(symbol='BNBBTC')

# place a test market buy order, to place an actual order use the create_order function
order = client.create_test_order(
    symbol='BNBBTC',
    side=Client.SIDE_BUY,
    type=Client.ORDER_TYPE_MARKET,
    quantity=100,
    recvWindow = 100000
)

# get all symbol prices
prices = client.get_all_tickers()



symbol = 'BTCUSDT'

def get_asset_balance(asset):
    res_dict = client.get_asset_balance(asset=asset)
    if not res_dict:
        return 0.0

    free_num = float(res_dict.get('free', 0.0))
    locked_num = float(res_dict.get('locked', 0.0))
    return free_num - locked_num

def test_simple():
# 获取余额
    get_asset_balance('BTC')

    # 获取1小时K线数据
    print client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1HOUR, limit=500)

    # # 市价买入, symbol: 交易对代码  quantity: 买入数量
    # client.order_market_buy(symbol=symbol, quantity=100)
    #
    # # 市价卖出, symbol: 交易对代码  quantity: 卖出数量
    # client.order_market_sell(symbol=symbol, quantity=100)
    #
    # # 限价买入, symbol: 交易对代码 price: 价格 quantity: 卖入数量
    # client.order_limit_buy(symbol=symbol, price=99999, quantity=100)
    #
    # # 限价卖出, symbol: 交易对代码 price: 价格 quantity: 卖出数量
    # client.order_limit_sell(symbol=symbol, price=99999, quantity=100)
# test_simple()

# withdraw 100 ETH
# check docs for assumptions around withdrawals
# from binance.exceptions import BinanceAPIException, BinanceWithdrawException
# try:
#     result = client.withdraw(
#         asset='ETH',
#         address='<eth_address>',
#         amount=100)
# except BinanceAPIException as e:
#     print(e)
# except BinanceWithdrawException as e:
#     print(e)
# else:
#     print("Success")
#
# # fetch list of withdrawals
# withdraws = client.get_withdraw_history()
#
# # fetch list of ETH withdrawals
# eth_withdraws = client.get_withdraw_history(asset='ETH')
#
# # get a deposit address for BTC
# address = client.get_deposit_address(asset='BTC')
#
# start aggregated trade websocket for BNBBTC
def process_message(msg):
    print("message type: {}".format(msg['e']))
    print(msg)
    # do something

from binance.websockets import BinanceSocketManager
bm = BinanceSocketManager(client)
bm.start_aggtrade_socket('ETHUSDT', process_message)
bm.start()
time.sleep(100000)

# get historical kline data from any date range

# fetch 1 minute klines for the last day up until now
# klines = client.get_historical_klines("BNBBTC", Client.KLINE_INTERVAL_1MINUTE, "1 day ago UTC")
#
# # fetch 30 minute klines for the last month of 2017
# klines = client.get_historical_klines("ETHBTC", Client.KLINE_INTERVAL_30MINUTE, "1 Dec, 2017", "1 Jan, 2018")
#
# # fetch weekly klines since it listed
# klines = client.get_historical_klines("NEOBTC", Client.KLINE_INTERVAL_1WEEK, "1 Jan, 2017")