# coding:utf-8

import time

from mantis.trade.constants import ServiceKeepAlivedTime
from mantis.trade.constants import *

from mantis.fundamental.application.app import instance

def get_service_live_time(redis,service_name):
    """
    查询指定服务程序的运行存活时间
    :param service_name:
    :return:
    """
    return get_service_status(redis,service_name).get('live_time',0)

def get_service_status(redis,service_name):
    """查询服务的运行状态信息"""
    return redis.hgetall()


def is_service_alive(live_time):
    return time.time() - live_time < ServiceKeepAlivedTime

def get_contract_detail(symbol):
    conn = instance.datasourceManager.get('redis').conn
    return conn.hget(CTAContractListKey,symbol)