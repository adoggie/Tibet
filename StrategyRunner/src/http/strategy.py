# coding: utf-8

from flask import request,g

from mantis.fundamental.application.app import instance
from mantis.fundamental.flask.webapi import CR


"""
策略控制
http控制接口，提供策略下发、运行监控、停止等

"""

def stop():
    """
    停止策略运行
    dispatcher发起停止时，先通知runner停止当前策略，同时通知launcher将runner进程kill
    """
    symbols = request.get_json()
    service = instance.serviceManager.get('main')
    service.subscribe(symbols)
    return CR().response

def status():
    """
    运行状态查询接口，监控程序访问此接口获知runner运行是否正常
    :return:
    """
    pass


