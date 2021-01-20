#!/usr/bin/python3
#-*-coding:utf8 -*-

import logging,os,sys
import time
import threading
import common.config as sconfig

log_path = os.getenv('LOG_PATH') or '/dev/null'
if not os.path.exists(os.path.dirname(log_path)):
    os.mkdir(os.path.dirname(log_path))

slog = logging.getLogger(log_path)

if sconfig.LOGLEVEL == 'debug':
    slog.setLevel(logging.DEBUG)
elif sconfig.LOGLEVEL == 'info':
    slog.setLevel(logging.INFO)
elif sconfig.LOGLEVEL == 'warn':
    slog.setLevel(logging.WARNING)
elif sconfig.LOGLEVEL == 'error':
    slog.setLevel(logging.ERROR)
elif sconfig.LOGLEVEL == 'critical':
    slog.setLevel(logging.CRITICAL)
else:
    slog.setLevel(logging.DEBUG)

'''
%(filename)s        调用日志输出函数的模块的文件名
%(module)s          调用日志输出函数的模块名
%(funcName)s        调用日志输出函数的函数名
%(lineno)d          调用日志输出函数的语句所在的代码行
'''
fmt = logging.Formatter('[%(asctime)s][%(process)d][%(thread)d][%(levelname)s][%(filename)s][%(funcName)s][%(lineno)d]:%(message)s', '%Y-%m-%d %H:%M:%S')

#设置CMD日志
sh = logging.StreamHandler()
sh.setFormatter(fmt)
sh.setLevel(logging.WARNING)
#设置文件日志
fh = logging.FileHandler(log_path)
fh.setFormatter(fmt)
fh.setLevel(logging.DEBUG)
slog.addHandler(sh)
slog.addHandler(fh)

def log_monitor():
    log_path = os.getenv('LOG_PATH')
    if not log_path:
        print("env LOG_PATH invlaid")
        return

    slog.info("log monitor begin")
    # just wait
    time.sleep(60 * 1)

    if not os.path.exists(log_path):
        print("{0} not exist".format(log_path))
        return

    log_max_size = 100 * 1024 * 1024 # 100MB
    while True:
        time.sleep(60)
        size = os.path.getsize(log_path)
        if size < log_max_size:
            continue
        open(log_path, 'w').close()

    return


def start_log_monitor():
    log_monitor_th = threading.Thread(target = log_monitor)
    log_monitor_th.daemon = True
    log_monitor_th.start()

if __name__ =='__main__':
    #slog = Logger('log/xx.log',logging.WARNING,logging.DEBUG)
    slog.debug('一个debug信息')
    slog.info('一个info信息')
    slog.warn('一个warning信息')
    slog.error('一个error信息')
    slog.critical('一个致命critical信息')

