#coding:utf-8


"""
author: sam
revision:
    1. create 2017/4/8
"""

from threading import Thread,Condition,Lock
import redis as Redis
from mantis.fundamental.utils.importutils import import_function


class MessageChannel(object):
    def __init__(self,cfgs,broker):
        self.cfgs = cfgs
        self.broker = broker
        self.message_handler = None

        self.name = cfgs.get('name')

        handler = cfgs.get('handler')
        if handler:
            self.message_handler = import_function(handler)  # importing functions dynamically

        self.topic = None
        self.producer = None
        self.consumer = None
        self.cond_readable = Condition()
        self.thread = None
        self.isclosed = True
        self.pubsub = None
        self.sub_handlers ={}


    @property
    def conn(self):
        return self.broker.conn

    def open(self):
        if self.message_handler:
            if self.cfgs.get('type') == 'pubsub':
                self.pubsub = self.conn.pubsub()
                self.pubsub.subscribe(self.name)
            self.thread = Thread(target=self.message_recieving())
            self.thread.start()

    def close(self):
        self.isclosed = True
        self.join()


    def join(self):
        if self.thread:
            self.thread.join()

    def produce(self,message):
        if self.cfgs.get('type') == 'queue':
            self.conn.rpush(self.name,message)

    def publish_or_produce(self,message):
        self.publish(message)
        self.produce(message)

    def consume(self,block=True,timeout=0):
        msg = self.conn.lpop(self.name)
        return msg

    # def subscribe(self,pattern, message_handler=None):
    #     self.message_handler = message_handler
    #     self.pubsub = self.conn.pubsub()
    #     # self.pubsub.psubscribe( pattern)
    #     self.pubsub.subscribe( pattern)
    #
    #
    #     if self.message_handler:
    #         self.thread = Thread(target=self.message_recieving(),args=(message_handler,))
    #         self.thread.start()
    #
    # def unsubscribe(self,pattern):
    #     pass


    def publish(self,message):
        if self.cfgs.get('type') == 'pubsub':
            self.conn.publish(self.name,message)

    def message_recieving(self):
        self.isclosed = False

        while not self.isclosed:
            if self.cfgs.get('type') == 'pubsub':
                message = self.pubsub.get_message()
            else:
                message = self.conn.blpop(self.name,0.1)
            if message is not None:
                ctx ={
                    "channel":self,
                }
                self.message_handler(message, ctx)



class MessageBroker(object):
    def __init__(self):
        self.cfgs = {}
        self.channels = {}
        self.conn = None

    def init(self,cfgs):
        self.cfgs = cfgs
        for cfg in self.cfgs.get('channels',[]):
            if cfg.get('enable', False) is False:
                continue
            self.channels[cfg.get('name')] = MessageChannel(cfg,self)

    def open(self):
        host = self.cfgs.get('host')
        port = self.cfgs.get('port')
        passwd = self.cfgs.get('password')
        db = self.cfgs.get('db')
        self.conn = Redis.StrictRedis(host, port, password=passwd, db=db)

        for _,channel in self.channels.items():
            channel.open()

    def close(self):
        for channel in self.channels:
            channel.close()

    def join(self):
        pass

    def get(self, name):
        return self.channels.get(name)

    def createChannel(self,name,handler=None,type_='queue'):
        chan = self.get(name)
        if not chan:
            cfgs = dict(name=name,handler=handler,type=type_)
            chan = MessageChannel(cfgs,self)
            self.channels[name] = chan
        return chan

    def createPubsubChannel(self,name,handler=None):
        return self.createChannel(name,handler,'pubsub')


