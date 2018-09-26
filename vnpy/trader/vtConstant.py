# encoding: UTF-8

from vnpy.trader.language import constant
# from vnpy.trader.language.chinese.constant import *
from vnpy.trader.language.english.constant import *

# 将常量定义添加到vtConstant.py的局部字典中
d = locals()
for name in dir(constant):
    if '__' not in name:
        d[name] = constant.__getattribute__(name)
