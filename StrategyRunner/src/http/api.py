#coding:utf-8

import json
from flask import Flask,request
from flask import Response

from flask import render_template
from mantis.fundamental.application.app import  instance
from mantis.fundamental.flask.webapi import *
from mantis.fundamental.flask.utils import nocache
from proxy import TradeAdapterProxy
from mantis.trade.types import ProductClass
from vnpy.trader.app.ctaStrategy.ctaBase import *
from .strategy import get_strategy_running_profile

def sendOrder():
    "POST"
    main = instance.serviceManager.get('main')
    controller = main.controller

    product_account = request.values.get('product_account')
    symbol = request.values.get('symbol')
    price = request.values.get('price')
    volumn = request.values.get('volumn')
    price = float(price)
    volumn = int(volumn)
    type = request.values.get('type') # buy,sell,short,cover

    ordertype = CTAORDER_BUY
    if type == 'sell':
        ordertype = CTAORDER_SELL
    if type == 'short':
        ordertype = CTAORDER_SHORT
    if type == 'cover':
        ordertype = CTAORDER_COVER

    product,account = product_account.split('.')

    orderids = []
    if product == ProductClass.Future:
        orderids = controller.futureHandler.sendOrder(symbol,ordertype,price,volumn,account=account)

    return CR().assign(orderids).response

def cancelOrder():
    """撤销订单 POST
    :param order_id:
    """
    main = instance.serviceManager.get('main')
    controller = main.controller

    order_id = request.values.get('order_id')
    product_account = request.values.get('product_account')
    product, account = product_account.split('.')

    if product == ProductClass.Future:
        controller.futureHandler.cancelOrder(order_id,account)
    return CR().response

def cancelAllOrders():
    """撤销所有订单 POST"""
    main = instance.serviceManager.get('main')
    controller = main.controller

    product_account = request.values.get('product_account')

    product, account = product_account.split('.')
    if product == ProductClass.Future:
        controller.futureHandler.cancelAllOrders() # 清除所有账号下的委托订单


    return CR().response

def cancelAllOrdersIgnoreAccount():
    """撤销所有订单 POST"""
    main = instance.serviceManager.get('main')
    controller = main.controller
    controller.cancelAllOrders()
    return CR().response

def sellOrCoverAllTrades():
    """一键平仓"""
    return CR().response

def strategy_start():
    """通知策略开始"""
    return CR().response

def strategy_stop():
    """通知策略停止"""
    return CR().response

def strategy_pause():
    """通知策略暂停"""
    return CR().response

def get_strategy_profile():
    """获取策略所有运行状态信息"""
    profiles = get_strategy_running_profile()
    return CR(result=profiles).response