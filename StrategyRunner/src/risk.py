# coding:utf-8

# risk.py
# 风险控制模块

from mantis.fundamental.utils.useful import singleton

# @singleton
class RiskManager(object):
    """
    风险控制模块
    控制发单、撤单等行为
    """
    def __init__(self,task):
        self.task = task


