# coding:utf-8

import json
import datetime
from mantis.fundamental.application.app import instance
from mantis.fundamental.utils.timeutils import datetime_to_timestamp
from mantis.trade.command import StrategyLogContent
from mantis.trade.message import Message

def strategy_log_handle(message,ctx):
    """
    """
    # message = Message(StrategyLogContent.NAME)
    msg = Message.unmarshall(message)
    if msg.name != StrategyLogContent.NAME:
        return
    service = instance.serviceManager.get('main')
    service.sendLogDetail(msg)
