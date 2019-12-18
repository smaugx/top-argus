#!/usr/bin/python3
#-*-coding:utf8 -*-

import logging,os
import common.config as sconfig

base_path = './log'
pid= os.getpid()
pid = 'xx'
path = os.path.join(base_path, 'topargus-{0}.log'.format(pid))
if not os.path.exists(base_path):
    os.mkdir(base_path)

slog = logging.getLogger(path)

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
fh = logging.FileHandler(path)
fh.setFormatter(fmt)
fh.setLevel(logging.DEBUG)
slog.addHandler(sh)
slog.addHandler(fh)

if __name__ =='__main__':
    #slog = Logger('log/xx.log',logging.WARNING,logging.DEBUG)
    slog.debug('一个debug信息')
    slog.info('一个info信息')
    slog.warn('一个warning信息')
    slog.error('一个error信息')
    slog.critical('一个致命critical信息')

