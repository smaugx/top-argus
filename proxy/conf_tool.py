#!/usr/bin/env python3
#! -*- coding:utf8 -*-

import os
import time
import requests
import copy
import json
import threading
import operator
import argparse

gconfig = {
        'global_sample_rate': 500,  # sample_rate%。  50%
        'alarm_pack_num': 2,   # upload alarm size one time
        'config_update_time': 5 * 60,  # 5 mins
        'grep_broadcast': {
            'start': 'true',
            'sample_rate': 100,  #20%
            'alarm_type': 'packet',
            'network_focus_on': ['ff0000010000','ff0000020000', 'ff00000f0101', 'ff00000e0101', 'ff00000001'], # src or dest: rec;zec;edg;arc;aud/val
            'network_ignore':   [],  # src or dest
            },
        'grep_point2point': {
            'start': 'true',
            'sample_rate': 10,   #1% 
            'alarm_type': 'packet',
            'network_focus_on': ['ff0000010000','ff0000020000', 'ff00000f0101', 'ff00000e0101', 'ff00000001'], # src or dest: rec;zec;edg;arc;aud/val
            'network_ignore':   [],  # src or dest
            },
        'grep_networksize': {
            'start': 'true',
            'sample_rate': 50,  #5%
            'alarm_type': 'networksize',
            },
        'system_cron': {
            'start': 'true',
            'alarm_type': 'system',
            },
        }

def update_config():
    global gconfig
    url = 'http://127.0.0.1:9091/api/config/'
    my_headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
            'Content-Type': 'application/json;charset=UTF-8',
            }
    payload = {
            'config': gconfig,
            'auth': 'smaugadmin',
            #'test': 'true',
            'test': 'false',
            }
    try:
        res = requests.put(url, headers = my_headers, data = json.dumps(payload), timeout = 5)
        if res.status_code == 200:
            if res.json().get('status') == 0:
                print("update remote config ok, response: {0}".format(json.dumps(res.json(), indent=4)))
                return True
            else:
                print('update remote config failed, response: {0}'.format(json.dumps(res.json(), indent= 4)))
                return False
    except Exception as e:
        print('update remote config exception: {0}'.format(e))
        return False

def get_config():
    url = 'http://127.0.0.1:9091/api/config/'
    my_headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
            'Content-Type': 'application/json;charset=UTF-8',
            }
    config = {}
    try:
        res = requests.get(url, headers = my_headers, timeout = 5)
        if res.status_code == 200:
            if res.json().get('status') == 0:
                print("get remote config ok, response: {0}".format(json.dumps(res.json(), indent = 4)))
                return True
    except Exception as e:
        print("exception: {0}".format(e))
        return False

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.description='TOP-Argus config tool，更新配置文件到配置中心，查看配置中心的配置文件'
    parser.add_argument('-u', '--update', help='update config server', default = 'false')
    parser.add_argument('-g', '--get',    help='get config from server', default = 'false')
    args = parser.parse_args()

    if args.update == 'true':
        update_config()

    if args.get == 'true':
        get_config()

    print('done')
