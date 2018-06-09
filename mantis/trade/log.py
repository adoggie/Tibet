# coding: utf-8

from logging import Handler

from mantis.fundamental.logging.handler import LogHandlerBase
from mantis.fundamental.logging.logger import Logger
from mantis.fundamental.application.app import instance

# class TradeServiceLogger(Logger):
#     def __init__(self,service):
#         name = "%s.%s"%(service.getServiceType(),service.getServiceId())
#         Logger.__init__(self,name)
#         self.service = service
#         self.channels =[]
#         cfgs = self.service.getConfig()
#         for dest in cfgs.get('logging',[]):
#             broker,channel,type_ = dest.get('name').split('/')
#             channel = channel.format(service_type = service.getServiceType(),
#                                      service_id = service.getServiceId())
#             brokerObj = instance.messageBrokerManager.get(broker)
#             chanObj = brokerObj.createChannel(channel,type_)
#             self.channels.append(chanObj)


class TradeServiceLogHandler(LogHandlerBase,Handler):
    """
    """
    TYPE = 'tradelogger'

    def __init__(self, service):
        Handler.__init__(self)
        LogHandlerBase.__init__(self)
        self.service = service


    def emit(self,record):
        msg = self.format(record)
        self.service.dataFanout('logging',msg)


__all__ = ( TradeServiceLogHandler,)