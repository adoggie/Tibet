# coding: utf-8

import json
from flask import request,g

from mantis.fundamental.application.app import instance
from mantis.fundamental.flask.webapi import CR,ErrorReturn
from mantis.trade.message import Message
from mantis.trade.errors import ErrorDefs
from mantis.trade import command
from vnpy.trader.vtObject import *

def handle_message():
    """
    统一处理发送进入的所有消息
    :return:
    """
    data = request.data
    message = Message.unmarshall(data)
    if not message:
        return ErrorReturn(ErrorDefs.ParameterInvalid).response

    if message.name == command.GetOrder.NAME:
        return message_getOrder(message)

    if message.name == command.GetAllWorkingOrders.NAME:
        return message_getAllWorkingOrders(message)

    if message.name == command.GetAllOrders.NAME:
        return message_getAllOrders(message)

    if message.name == command.GetAllTrades.NAME:
        return message_getAllTrades(message)

    if message.name == command.GetAllPositions.NAME:
        return message_getAllPositions(message)

    if message.name == command.GetAllAccounts.NAME:
        return message_getAllAccounts(message)

    if message.name == command.SendOrder.NAME:
        return message_sendOrder(message)

    if message.name == command.CancelOrder.NAME:
        return message_cancelOrder(message)

    return ErrorReturn(ErrorDefs.ParameterInvalid).response


def message_sendOrder(message):
    de = instance.serviceManager.get('main').dataEngine
    m = command.SendOrder()
    m.__dict__ = message.data

    orderIds = de.sendOrder(m)
    cr = CR()
    result = orderIds
    cr.assign(result)
    return cr.response

def message_cancelOrder(message):
    de = instance.serviceManager.get('main').dataEngine
    m = command.CancelOrder()
    m.__dict__ = message.data
    result = de.cancelOrder(m.order_id)
    if result:
        return CR().response
    return ErrorReturn(ErrorDefs.Error).response

def message_getOrder(message):
    de = instance.serviceManager.get('main').dataEngine
    m = command.GetOrder()
    m.__dict__ = message.data
    order = de.getOrder(m.order_id)
    cr = CR()
    if order:
        cr.assign(order.__dict__)
    return cr.response

def message_getAllWorkingOrders(message):
    de = instance.serviceManager.get('main').dataEngine
    orders = de.GetAllWorkingOrders()
    cr = CR()
    result =[]
    for order in orders:
        result.append(order.__dict__)
    cr.assign(result)
    return cr.response

def message_getAllOrders(message):
    de = instance.serviceManager.get('main').dataEngine
    orders = de.getAllOrders()
    cr = CR()
    result =[]
    for order in orders:
        result.append(order.__dict__)
    cr.assign(result)
    return cr.response

def message_getAllTrades(message):
    de = instance.serviceManager.get('main').dataEngine
    trades = de.getAllTrades()
    cr = CR()
    result =[]
    for trade in trades:
        result.append(trade.__dict__)
    cr.assign(result)
    return cr.response

def message_getAllPositions(message):
    de = instance.serviceManager.get('main').dataEngine
    positions = de.getAllPositions()
    cr = CR()
    result =[]
    for pos in positions:
        result.append(pos.__dict__)
    cr.assign(result)
    return cr.response

def message_getAllAccounts(message):
    de = instance.serviceManager.get('main').dataEngine
    accounts = de.getAllAccounts()
    cr = CR()
    result =[]
    for acc in accounts:
        result.append(acc.__dict__)
    cr.assign(result)
    return cr.response



