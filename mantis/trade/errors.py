#coding: utf-8

from mantis.fundamental.errors import ErrorEntry

class ErrorDefs(object):
    OK                  = ErrorEntry(0,u'succ')
    ParameterInvalid    = ErrorEntry(1,u'参数无效')
    BAR_SCALE_INVALID   = ErrorEntry(1001,u'k线时间刻度规格错误')
