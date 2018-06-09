# coding: utf-8

from flask import request,g

from mantis.fundamental.application.app import instance
from mantis.fundamental.flask.webapi import CR

def list_contracts():
    """
    列举所有已订阅的合约代码
    :return:
    """
    service = instance.serviceManager.get('main')
    symbols = service.getSymbols()
    return  CR().assign(symbols).response

def subscribe():
    """
    订阅指定的合约代码
    :return:
    """
    symbols = request.get_json()
    service = instance.serviceManager.get('main')
    service.subscribe(symbols)
    return CR().response

def unsubscribe():
    pass


