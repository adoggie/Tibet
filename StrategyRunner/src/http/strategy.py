# coding: utf-8

from flask import request,g

from mantis.fundamental.application.app import instance
from mantis.fundamental.flask.webapi import CR


"""
策略控制
http控制接口，提供策略下发、运行监控、停止等

"""

def get_strategy_running_profile():
    """获取策略所有运行状态信息"""
    main = instance.serviceManager.get('main')
    controller = main.controller

    profiles = {
        "service_id": main.service_id,
        "service_type": str(main.service_type),
        "futures": {
            "accounts": [
                {}
            ]
        }
    }

    accounts = []
    for q in controller.futureHandler.accounts.values():
        item = {
            "account": q.account,
            "product": q.product,
            "name": q.name,
            "limit": q.limit,
            "proxy": None,  # q.trade_proxy,
            "data": ''  # trade_query(q.trade_proxy)
        }
        if q.trade_proxy:
            item['data'] = trade_query(q.trade_proxy)
            item['proxy_http'] = q.trade_proxy.http
        accounts.append(item)

    profiles['futures']['accounts'] = accounts
    return profiles

def trade_query(proxy):
    result ={}

    result['currentaccount'] = proxy.getCurrentAccount().__dict__

    result['positions'] = []
    for pos in proxy.getAllPositions():
        result['positions'].append( pos.__dict__ )

    result['orders'] = []
    for order in proxy.getAllWorkingOrders():
        result['orders'].append( order.__dict__ )

    result['trades'] = []
    for trade in proxy.getAllTrades():
        result['trades'].append( trade.__dict__ )
    return result
