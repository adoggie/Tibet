# coding: utf-8

from datetime import datetime, timedelta, time
import traceback

MORNING_START = time(9, 0)
MORNING_REST = time(10, 15)
MORNING_RESTART = time(10, 30)
MORNING_END = time(11, 30)
AFTERNOON_START = time(13, 30)
AFTERNOON_END = time(15, 0)
NIGHT_START = time(21, 0)
NIGHT_END = time(2, 30)

class CtpTickValidator(object):
    """期货行情数据校验"""
    def __init__(self):
        pass

    def validate(self,tick):
        return tick

    def _validate(self,tick):
        """暂时不启用"""
        try:
            tick = self.checkData(tick)
        except:
            traceback.print_exc()
        return tick

    def checkData(self,tick):
        dt = tick['datetime']
        if ((MORNING_START <= dt < MORNING_REST) or
                (MORNING_RESTART <= dt < MORNING_END) or
                (AFTERNOON_START <= dt < AFTERNOON_END) or
                (dt >= NIGHT_START) or
                (dt < NIGHT_END)):
            return tick
        return None