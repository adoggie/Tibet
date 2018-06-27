#coding:utf-8


from mantis.fundamental.application.use_gevent import use_gevent
# use_gevent()
from mantis.fundamental.application.app import Application,instance,setup

class TradeApplication(Application):
    def __init__(self):
        Application.__init__(self)

    def initOptions(self):
        pass

setup(TradeApplication).init().run()



