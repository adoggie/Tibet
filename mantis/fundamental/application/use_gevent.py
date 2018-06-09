#coding:utf-8

import gevent
from gevent import monkey
monkey.patch_all(Event=True)
from gevent.event import Event
