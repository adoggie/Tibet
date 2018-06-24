# coding:utf-8

import threading
import redlock


class Locker(object):
    def __init__(self,resource,ttl=0,servers=[{"host": "localhost", "port": 6379, "db": 0}, ]):
        self.servers = servers
        self.resource = resource
        self.ttl = ttl

        self.dlm = None
        self.r = None

    def lock(self):
        self.dlm = redlock.Redlock(self.servers)
        self.r = self.dlm.lock( self.resource,self.ttl)
        if not self.r:
            return False
        return True

    def unlock(self):
        self.dlm.unlock(self.r)




