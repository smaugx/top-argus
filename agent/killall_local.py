#!/usr/bin/env python
#-*- coding:utf8 -*-


import os

def killall_logwatch():
    cmd = 'ps -ef |grep argus_agent.py |grep -v grep'
    result = os.popen(cmd).readlines()
    if not result:
        return
    print(result)
    for item in result:
        sp = item.split()
        if len(sp) < 2:
            continue
        killcmd = 'kill -9 {0}'.format(sp[1])
        print(killcmd)
        os.popen(killcmd)
    
    result = os.popen(cmd).readlines()
    if not result:
        return
    print(result)
    return
  

killall_logwatch()
