# coding:utf-8

import traceback
import json
from collections import OrderedDict

class Request(object):
    def __init__(self, name='', data={},ref_id='',back_url=''):
        self.type       = 'request'
        self.name       = name
        self.data       = data
        self.header     = {'ref_id':ref_id,'back_url':back_url}


    def marshall(self):
        message = OrderedDict(type='request',name = self.name,
                              header=self.header,
                              body=self.data
                              )
        return json.dumps(message)

    def send(self,channel):
        channel.publish_or_produce(self.marshall())

    @staticmethod
    def unmarshall(data):

        if not isinstance(data,dict):
            data = json.loads(data)

        req = None
        try:
            req = Request()
            req.name = data.get('name','')
            req.data = data.get('body',{})
            req.ref_id = data.get('header',{}).get('ref_id','')
            req.back_url = data.get('header',{}).get('back_url','')
        except:
            traceback.print_exc()
            req = None
        return req


class Response(object):
    def __init__(self,data ={} ,request =None):
        self.type       = 'response'
        self.data       = data
        self.header     = {'ref_id',''}
        self.name       = ''
        if request:
            self.header = request.header
            self.name   = request.name


    def marshall(self):

        message = OrderedDict(type='response',
                              name = self.name,
                              header=self.header,
                              body=self.data
                              )
        return json.dumps(message)

    @staticmethod
    def unmarshall(data):
        if not isinstance(data, dict):
            data = json.loads(data)

        resp = None
        try:
            resp = Request()
            resp.name = data.get('name', '')
            resp.data = data.get('body', {})
            resp.ref_id = data.get('header', {}).get('ref_id', '')
        except:
            traceback.print_exc()
            resp = None
        return resp

class RequestOrResponse(object):
    @staticmethod
    def parse(data):
        message = json.loads(data)
        if message.get('type') == 'request':
            return Request.unmarshall(message)
        if message.get('type') == 'response':
            return Response.unmarshall(message)
        return None
