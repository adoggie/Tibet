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
    instance.getLogger().debug(' call list_contracts()..')
    return  CR().assign(symbols).response

def subscribe():
    """
    订阅指定的合约代码
    :return:
    """
    symbols = request.get_json()
    service = instance.serviceManager.get('main')
    service.subscribe(*symbols)
    instance.getLogger().debug( str(symbols) )
    return CR().response

def unsubscribe():
    pass

def ticks():
    service = instance.serviceManager.get('main')
    result= dict(count=service.ticks_counter,ticks=service.ticks_samples)
    return CR().assign(result).response
"""
curl -l -H "Content-type: application/json" -X POST -d '["a","b","c"]' http://172.16.109.237:18901
"""


