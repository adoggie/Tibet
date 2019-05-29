#coding:utf-8

import json
import time
import datetime
import os.path
import os
from dateutil.parser import parse

from collections import OrderedDict
from flask import Flask,request,g
from flask import Response
import requests
import base64
from StringIO import StringIO

from flask import render_template
from mantis.fundamental.application.app import  instance
from mantis.fundamental.utils.useful import cleaned_json_data


from mantis.fundamental.flask.webapi import ErrorReturn,CR
from mantis.fundamental.utils.timeutils import current_datetime_string,timestamp_current,timestamp_to_str
from token import token_encode
from token import  login_check
from mantis.sg.fisher.model import model
from AliceBackend.errors import ErrorDefs

def hello():
    """写下第一个webapi """
    ip= request.remote_addr
    result = []
    return CR(result = result)

def get_trade_days():
    conn = instance.datasourceManager.get('mongodb').conn
    names = conn.database_names()
    names = filter(lambda _:_.find('TradeFisher_')!=-1 , names)
    names = map(lambda  _: _.split('_')[1], names)
    return CR(result= names).response

def get_strategy_list():
    date_s = request.values.get('date','')
    if not date_s:
        return ErrorReturn(ErrorDefs.ParameterInvalid).response
    date = parse(date_s)
    conn = instance.datasourceManager.get('mongodb').conn
    dbname = 'TradeFisher_{}-{}-{}'.format(date.year,date.month,date.day)
    db = conn[dbname]
    model.StrategyParam.__database__ = db
    sts = model.StrategyParam.find()
    result = []
    for s in sts:
        s.date = date_s
        result.append( s.dict())
    return CR(result=result).response


"""
http://localhost:7788/fisher/api/strategy/code/list?date=2019-5-15&strategy_id=AJ_ZF_InDay
"""
def get_code_list():
    date = request.values.get('date', '')
    strategy_id = request.values.get('strategy_id')
    if not strategy_id or not date :
        return ErrorReturn(ErrorDefs.ParameterInvalid).response

    date = parse(date)
    conn = instance.datasourceManager.get('mongodb').conn
    dbname = 'TradeFisher_{}-{}-{}'.format(date.year, date.month, date.day)
    db = conn[dbname]
    model.CodeSettings.__database__ = db
    model.CodePrice.__database__ = db
    model.CodePosition.__database__ = db
    result = []
    for cs in model.CodeSettings.find(strategy_id = strategy_id):
        data = cs.dict()
        price = model.CodePrice.get(code = cs.code)
        if price:
            data['price'] =  price.dict()
            data['price']['time'] = str(data['price']['time'])
        pos = model.CodePosition.get(strategy_id = strategy_id , code = cs.code)
        if pos:
            data['pos'] = pos.dict()
        result.append( data )
    return CR(result = result).response

"""
http://localhost:7788/fisher/api/strategy/code/logs?date=2019-5-15&strategy_id=AJ_ZF_InDay&code=002367

"""
def get_code_trade_logs():
    date = request.values.get('date', '')
    strategy_id = request.values.get('strategy_id')
    code = request.values.get('code')
    if not strategy_id or not date:
        return ErrorReturn(ErrorDefs.ParameterInvalid).response
    date = parse(date)
    conn = instance.datasourceManager.get('mongodb').conn
    dbname = 'TradeFisher_{}-{}-{}'.format(date.year, date.month, date.day)
    db = conn[dbname]
    coll = db[strategy_id]
    rs = coll.find({'code':code}).sort('time',-1)
    result = []
    for r in list(rs):
        r['time'] = str(r['time'])
        del r['_id']
        result.append(r)
    return CR(result = result).response
