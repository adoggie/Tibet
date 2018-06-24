# coding: utf-8


class CommandBase(object):
    def __init__(self,name):
        self.name = name


    def marshall(self):
        pass

    def unmarshall(self):
        pass


class FutureCommandSet(object):
    ORDER_SELL = 'sell'
    ORDER_SHORT = 'short'
    ORDER_COVER = 'cover'
    ORDER_CANCEL = 'cancel'

    def __init__(self):
        pass



class StockCommandSet(object):
    def __init__(self):
        pass


