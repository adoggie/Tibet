#coding:utf-8

from mantis.fundamental.utils.useful import singleton
from mantis.fundamental.application.app import instance
from mantis.BlueEarth.constants import DeviceCommandQueue

def sendCommand(device_id,device_type,command,ds='redis'):
    """
    在线设备即刻发送，离线设备寄存发送命令
    """
    key = DeviceCommandQueue.format(device_type = device_type,device_id=device_id)
    redis = instance.datasourceManager.get(ds).conn
    data = ''
    if isinstance(command,(str,unicode)):
        data = command.encode('utf-8')
    else:
        # data = command.bytes()
        pass
    redis.rpush(key,data)

# @singleton
class RedisIdGenerator(object):
    """交易请求流水号生成器"""
    def __init__(self):
        self.req_id = 0
        self.redis = None
        self.service = None
        self.key = ''
        self.incr = 1

    def init(self,key,incr = 1):
        """从db/redis加载当前的值"""
        self.key = key
        self.incr = incr
        return self

    def next_id(self):
        """提供策略使用的request-id"""
        self.redis = instance.datasourceManager.get('redis').conn
        self.service = instance.serviceManager.get('main')
        request_id = self.redis.incrby(self.key,self.incr)
        return request_id

    next = next_id