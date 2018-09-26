#coding:utf-8

import multiprocessing
from time import sleep
import time,os
from datetime import datetime, time as Time

# ----------------------------------------------------------------------

def log_print(msg):
    print time.asctime(), msg

# ----------------------------------------------------------------------
def runChildProcess():
    """子进程运行函数"""
    print '-' * 20

    cmd = 'python server-ctp-market.py'
    os.system(cmd)


def killProcess():
    cmd = 'cat ../run/server.pid | xargs kill -9'
    os.system(cmd)
# ----------------------------------------------------------------------
def runParentProcess():
    """父进程运行函数"""

    DAY_START = Time(8, 57)  # 日盘启动和停止时间
    DAY_END = Time(15, 18)
    NIGHT_START = Time(20, 57)  # 夜盘启动和停止时间
    # NIGHT_START = Time(20, 57)  # 夜盘启动和停止时间
    NIGHT_END = Time(2, 33)
    # NIGHT_END = Time(22, 31)

    p = None  # 子进程句柄

    while True:
        currentTime = datetime.now().time()
        recording = False

        # 判断当前处于的时间段
        if ((currentTime >= DAY_START and currentTime <= DAY_END) or
                (currentTime >= NIGHT_START ) or
                (currentTime <= NIGHT_END) ):
            recording = True

        # 过滤周末时间段：周六全天，周五夜盘，周日日盘
        # if ((datetime.today().weekday() == 6) or
        #         (datetime.today().weekday() == 5 and currentTime > NIGHT_END) or
        #         (datetime.today().weekday() == 0 and currentTime < DAY_START)):
        #     recording = False

        # 记录时间则需要启动子进程
        if recording and p is None:
            log_print( 'Start Child Process..')
            p = multiprocessing.Process(target=runChildProcess)
            p.start()
            log_print('Start Successful.')

        # 非记录时间则退出子进程
        if not recording and p is not None:
            # le.info(u'关闭子进程')
            log_print( 'Close Child Process ..' )
            p.terminate()
            p.join()
            p = None
            killProcess()
            log_print('Close Child Successful.')

        sleep(5)
        log_print("keep Watching..")


if __name__ == '__main__':
    # runChildProcess()
    runParentProcess()
