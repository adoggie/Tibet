#coding:utf-8

import inspect
from collections import OrderedDict
from mantis.fundamental.utils.importutils import import_module


class SymbolMatched(object):
    def __init__(self,matches,must=0,optional=0):
        """
        :param matches:
        :param must: 必填参数个数
        :param optional: 可选参数个数
        """
        self.matches = matches  # 匹配的符号名称列表
        # self.var = None         # 匹配上的模块属性
        self.name = None        # 符号名称
        # self.varnames = []      # hold arguments for function
        self.module = None
        # self.defined = False

    @property
    def var(self):
        return getattr(self.module,self.name)

    def isDefined(self):
        return self.name

    def isfunction(self):

        return inspect.isfunction( self.var )

    def function_arguments(self):
        funcs = {}

        for name,func in  inspect.getmembers(self.var,inspect.isfunction):
            funcs[name] = func.__code__.co_varnames

    def arguments(self):
        """返回函数对象的参数名称"""

        if inspect.isfunction(self.var):
            return self.var.__code__.co_varnames
        return []

    def matched(self,name):
        """检查name是否在匹配模式列表"""
        if self.matches.count(name.lower()) == 0:
            return False
        return True

    def __call__(self, *args, **kwargs):
        self.var(*args,**kwargs)
    # def match(self,mo):

class SymbolTable(object):
    """ 动态加载策略运行模块
        策略模块定义符号表,可以是变量或函数
    """
    def __init__(self):
        self.symbols = OrderedDict()

        self.initTable()

    def initTable(self):
        """ 支持多种匹配的符号名称定义
            支持策略模块中的多符号名称映射，且不区分大小写，当Controller触发相应事件时在symbolTable定位回调对象
        """
        self.symbols['ctx']     = SymbolMatched(['ctx','context'],0,0)  #
        self.symbols['init']    = SymbolMatched(['oninit','init','on_init'],0,1)  #
        self.symbols['start']   = SymbolMatched(['onstart','start','on_start'],0,1)  #
        self.symbols['stop']    = SymbolMatched(['onstop','stop','on_stop'],0,1)  #
        self.symbols['ontick']  = SymbolMatched(['ontick','on_tick'],1,1)  #
        self.symbols['onbar']   = SymbolMatched(['onbar','on_bar'],1,1)  #
        self.symbols['onorder'] = SymbolMatched(['onorder','on_order'],1,1)  #
        self.symbols['ontrade'] = SymbolMatched(['ontrade','on_trade'],1,1)  #
        self.symbols['ontimer'] = SymbolMatched(['ontimer','on_timer'],1,1)  #


    def loadModule(self,module_name):
        module = import_module(module_name)
        members = OrderedDict()
        symbols = dir(module)
        for name in symbols:
            if name.startswith('__'):
                continue
            members[name] = getattr(module,name) # 读取所有模块内的符号对象

        for name,member in members.items():
            for _,sm in self.symbols.items():   #符号名匹配
               if sm.matched(name):
                   sm.name = name
                   sm.module = module

        #
        print self.symbols
        # for s in self.symbols.values():
        #     print s.name,s.var

    def get(self,name):
        return self.symbols.get(name)

    def invoke(self,name,*args):
        func = self.get(name)
        if func.isDefined():
            args = args[:len(func.arguments())]
            func(*args)

            # if len(func.arguments()):
            #     func(*args)
            # else:
            #     func()


__all__ = (SymbolTable,SymbolMatched)