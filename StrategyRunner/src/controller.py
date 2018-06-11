# coding:utf-8

import inspect
from mantis.fundamental.utils.importutils import import_module


class SymbolMatched(object):
    def __init__(self,matches):
        self.matches = matches
        self.var = None
        self.name = None
        self.varnames = []  # hold arguments for function

    def isfunction(self):
        return inspect.isfunction(self.var)

    def function_arguments(self):
        funcs = {}
        for name,func in  inspect.getmembers(self.var,inspect.isfunction):
            funcs[name] = func.__code__.co_varnames

    def arguments(self):
        if inspect.isfunction(self.var):
            return self.var.__code__.co_varnames
        return []

    def matched(self,name):
        if self.matches.count(name.lower()) == 0:
            return False
        return True

    # def match(self,mo):

class SymbolTable(object):
    def __init__(self):
        self.symbols = {}

        self.initTable()

    def initTable(self):
        self.symbols['ctx'] = SymbolMatched(['ctx','context'])  # k
        self.symbols['init'] = SymbolMatched(['oninit','init','on_init'])  # k

    def loadModule(self,mod_name):
        mod = import_module(mod_name)
        members ={}
        symbols = dir(mod)
        for name in symbols:
            if name.startswith('__'):
                continue
            members[name] = getattr(mod,name)

        for name,member in members.items():
            for _,sm in self.symbols.items():
               if sm.matched(name):
                   sm.var = member
                   sm.name = name

        for s in self.symbols.values():
            print s.name,s.var




    def get(self,name):
        return self.methods.get(name)

class Strategy(object):
    def __init__(self):
        self.symbolTable = SymbolTable()

class StrategyController(object):
    def __init__(self,service):
        self.service = service
        self.table = SymbolTable()

    @property
    def dataResService(self):
        pass

    @property
    def marketService(self):
        pass

    @property
    def tradeService(self):
        pass

    def createTimer(self,action,timeout=1):
        task = self.service.registerTimedTask(action,timeout=timeout)
        return task

    def loadStrategy(self,module_name):
        self.table.loadModule('strategies.'+module_name)




if __name__ == '__main__':
    mod = StrategyController(None).loadStrategy('strategy_example')
    print dir(mod)