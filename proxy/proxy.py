#!/usr/bin/env python
#-*- coding:utf8 -*-

import os 
now_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(now_dir)  #parent dir
activate_this = '%s/vvlinux/bin/activate_this.py' % base_dir
exec(open(activate_this).read())

import sys
sys.path.insert(0, base_dir)

from flask import Flask ,request, url_for, render_template,jsonify
import sys
import json
import requests
import redis
import uuid
import time
import base64
import copy
import core
import threading
from common.slogging import slog

app = Flask(__name__)
alarm_entity = core.Alarm()

gconfig = {
        'watch_filename': './xtop.log',
        'global_sample_rate': 100,  # sample_rate%
        'alarm_pack_num': 1,   # upload alarm size one time
        'grep_broadcast': {
            'start': 'true',
            'sample_rate': 100,
            'network_focus_on': ['660000', '680000', '690000'], # src or dest
            'network_ignore':   ['670000'],  # src or dest
            },
        'grep_point2point': {
            'start': 'false',
            'sample_rate': 100,
            'network_focus_on': ['660000', '680000', '690000'], # src or dest
            'network_ignore':   ['670000'],  # src or dest
            },
        'grep_networksize': {
            'start': 'true',
            'sample_rate': 100,
            'network_focus_on': ['660000', '680000', '690000'], # src or dest
            'network_ignore':   ['670000'],  # src or dest
            },
        }

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/index', methods=['GET'])
@app.route('/index/', methods=['GET'])
def index():
    return 'Hello, World!'

# config get and update
@app.route('/api/alarm/', methods=['GET', 'POST'])
@app.route('/api/alarm', methods=['GET', 'POST'])
def config_update():
    global gconfig
    if not request.is_json:
        payload = json.loads(request.data)
    else:
        payload = request.get_json()

    ret = {'status':''}
    status_ret = {
            0:'OK',
            -1:'上报字段不合法,部分可能上传失败',
            -2:'格式转化出错，请检查字段数或者字段格式等'
            }

    alarm_ip = request.remote_addr
    slog.info("update config ip:{0} {1}".format(alarm_ip))
    ret = {'status': 0, 'error': status_ret.get(0), 'config': gconfig}
    return jsonify(ret)


#告警上报(发包收包情况收集)
@app.route('/api/alarm/', methods=['POST'])
@app.route('/api/alarm', methods=['POST'])
def alarm_report():
    payload = []
    if not request.is_json:
        payload = json.loads(request.data)
    else:
        payload = request.get_json()

    ret = {'status':''}
    status_ret = {
            0:'OK',
            -1:'上报字段不合法,部分可能上传失败',
            -2:'格式转化出错，请检查字段数或者字段格式等'
            }
    if len(payload) <= 0:
        ret = {'status': -2, 'error': status_ret.get(-2)}
        return jsonify(ret)

    first_item = payload[0]
    if not first_item.get('local_node_id'):   #TODO(smaug)
        ret = {'status': -1, 'error': status_ret.get(-1)}
        return jsonify(ret)

    alarm_ip = request.remote_addr
    #slog.info("recv ip:{0} {1} alarm:{2}".format(alarm_ip, len(payload), json.dumps(payload[0])))
    slog.info("recv ip:{0} {1} alarm:{2}".format(alarm_ip, len(payload), json.dumps(payload)))
    alarm_entity.handle_alarm(payload, alarm_ip)
    ret = {'status': 0, 'error': status_ret.get(0)}
    return jsonify(ret)

@app.route('/api/web/hash/<chain_hash>/', methods = ['GET'])
@app.route('/api/web/hash/<chain_hash>', methods = ['GET'])
def alarm_query(chain_hash):
    status_ret = {
            0:'OK',
            -1:'hash not exist',
            -2: 'hash invalid',
            }

    if not chain_hash:
        ret = {'status': -1, 'error': status_ret.get(-1)}
        return jsonify(ret)

    try:
        chain_hash = int(chain_hash)
    except Exception as e:
        ret = {'status': -2, 'error': status_ret.get(-2)}
        return jsonify(ret)

    slog.info("query hash: {0}".format(chain_hash))
    packet_info = alarm_entity.get_chain_hash(chain_hash)
    if not packet_info:
        ret = {'status': -1, 'error': status_ret.get(-1)}
        return jsonify(ret)
    ret = {'status':0,'error': status_ret.get(0), 'packet_info': packet_info}
    return jsonify(ret)


def run():
    global alarm_th
    # thread handle alarm and merge packet_info
    alarm_th = threading.Thread(target = alarm_entity.consume_alarm)
    alarm_th.start()

    # thread dump to db
    dumpdb_th = threading.Thread(target = alarm_entity.dump_db)
    dumpdb_th.start()

    app.run(host="0.0.0.0", port= 9090, debug=True)
    alarm_th.join()





if __name__ == '__main__':
    run()
