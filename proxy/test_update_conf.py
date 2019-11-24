#!/usr/bin/env python3
#! -*- coding:utf8 -*-

import os
now_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(now_dir)  #parent dir
activate_this = '%s/vvlinux/bin/activate_this.py' % base_dir
exec(open(activate_this).read())

import sys
sys.path.insert(0, base_dir)


import time
import requests
import copy
import json
import threading
import operator

gconfig = {
        'watch_filename': './xtop.log',
        'global_sample_rate': 100,  # sample_rate%
        'alarm_pack_num': 1,   # upload alarm size one time
        'grep_broadcast': {
            'start': 'true',
            'sample_rate': 100,
            'alarm_type': 'packet',
            'network_focus_on': ['660000', '680000', '690000'], # src or dest
            'network_ignore':   ['670000'],  # src or dest
            },
        'grep_point2point': {
            'start': 'false',
            'sample_rate': 100,
            'alarm_type': 'packet',
            'network_focus_on': ['660000', '680000', '690000'], # src or dest
            'network_ignore':   ['670000'],  # src or dest
            },
        'grep_networksize': {
            'start': 'true',
            'sample_rate': 100,
            'alarm_type': 'networksize',
            'network_focus_on': ['660000', '680000', '690000'], # src or dest
            'network_ignore':   ['670000'],  # src or dest
            },
        }

def update_config():
    global gconfig
    url = 'http://127.0.0.1:9090/api/config/'
    my_headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
            'Content-Type': 'application/json;charset=UTF-8',
            }
    payload = {
            'config': gconfig,
            'auth': 'smaugadmin',
            'test': 'true',
            }
    try:
        res = requests.put(url, headers = my_headers, data = json.dumps(payload), timeout = 5)
        if res.status_code == 200:
            if res.json().get('status') == 0:
                print("update remote config ok, response: {0}".format(res.text))
                return True
            else:
                print('update remote config failed, response: {0}'.format(res.text))
                return False
    except Exception as e:
        print('update remote config exception: {0}'.format(e))
        return False


    
if __name__ == "__main__":
    update_config()