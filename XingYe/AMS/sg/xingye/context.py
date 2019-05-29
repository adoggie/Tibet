#coding:utf-8

# @Singleton
from utils.importutils import import_module
from utils.useful import singleton
class ResTable:
    def __init__(self):
        OrderItem = None

@singleton
class Context:
    def __init__(self):
        self.Market = None
        self.Strategy = None
        self.ResTable = ResTable()
        self.data ={}

    def init(self,market,strategy):
        import main

        self.Market = market
        self.Strategy = strategy

        return self

    def launch(self,name):
        module = import_module(name)
        module.context = self
        module.init()
    
"""
from sg.xingye.context import Context
Context().init(Market,Strategy).launch(sname)



from sg.xingye.context import Context
Context().init(Market,Strategy)
Context().ResTable.OrderItem = OrderItem
Context().launch('sg.xingye.test')

sname=sg.xingye.main

"""


