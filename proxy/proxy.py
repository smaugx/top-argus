#!/usr/bin/env python
#-*- coding:utf8 -*-

from flask import Flask ,request, url_for, render_template,jsonify
import sys
import json
import requests
import copy

import os
project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(project_path))
log_path = os.path.join(project_path, "log/topargus-proxy.log")
os.environ['LOG_PATH'] =  log_path
from common.slogging import slog
import common.slogging as slogging


import common.my_queue as my_queue
import common.config as sconfig

app = Flask(__name__)
#mq = my_queue.CacheQueue()
mq = my_queue.RedisQueue(host= sconfig.REDIS_HOST, port=sconfig.REDIS_PORT, password=sconfig.REDIS_PASS)
gconfig_shm_file = sconfig.SHM_GCONFIG_FILE


gconfig = sconfig.PROXY_CONFIG

def dump_gconfig():
    global gconfig, gconfig_shm_file
    with open(gconfig_shm_file,'w') as fout:
        fout.write(json.dumps(gconfig))
        slog.info('dump gconfig:{0} to file:{1}'.format(json.dumps(gconfig), gconfig_shm_file))
        fout.close()
    return

def load_gconfig():
    global gconfig_shm_file
    new_config = None
    with open(gconfig_shm_file,'r') as fin:
        new_config = json.loads(fin.read())
        fin.close()
    return new_config

dump_gconfig()

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/index', methods=['GET'])
@app.route('/index/', methods=['GET'])
def index():
    return 'Hello, World!'

# config get and update
@app.route('/api/config/', methods=['GET', 'PUT'])
@app.route('/api/config', methods=['GET', 'PUT'])
def config_update():
    alarm_ip = request.headers.get('X-Forwarded-For') or request.headers.get('X-Real-IP') or request.remote_addr
    slog.info("/api/config clientip:{0} method:{1}".format(alarm_ip, request.method))
    global gconfig
    status_ret = {
            0:'OK',
            -1:'权限验证失败',
            -2:'格式转化出错，请检查字段数或者字段格式等',
            -3: '不支持的方法',
            }
    ret = {}
    if request.method == 'GET':
        new_config = load_gconfig()
        if new_config:
            gconfig = copy.deepcopy(new_config)
            slog.debug('load gconfig from shm:{0}'.format(json.dumps(gconfig)))
        ret = {'status': 0, 'error': status_ret.get(0), 'config': gconfig, 'ip': alarm_ip}
        return jsonify(ret)

    if request.method == 'PUT':
        payload = {}
        if not request.is_json:
            payload = json.loads(request.data)
        else:
            payload = request.get_json()

        # auth verify
        if not payload or payload.get('auth') != 'smaugadmin':
            ret['status'] = -1
            ret['error'] = status_ret.get(-1)
            return jsonify(ret)
        
        config = payload.get('config')
        if not config:
            ret['status'] = -2
            ret['error'] = status_ret.get(-2)
            return jsonify(ret)
        if payload.get('test') == 'true':
            out = '[test] update config: {0}, old_config: {1}'.format(json.dumps(config, indent = 4), json.dumps(gconfig, indent = 4))
            print(out)
            slog.info(out)
            ret['status'] = 0
            ret['error'] = status_ret.get(0)
            ret['config'] = config
            return jsonify(ret)
        if payload.get('test') == 'false':
            out = 'update config: {0}, old_config: {1}'.format(json.dumps(config, indent = 4), json.dumps(gconfig, indent = 4))
            print(out)
            slog.info(out)
            gconfig = copy.deepcopy(config)
            dump_gconfig()   # dump to shm
            slog.info('udpate config finished, config is: {0}'.format(json.dumps(gconfig, indent = 4)))
            ret['status'] = 0
            ret['error'] = status_ret.get(0)
            ret['config'] = config
            return jsonify(ret)

    ret['status'] = -3
    ret['error'] = status_ret.get(-3)
    slog.info('not supported method:{0} of /api/config'.format(request.method))
    return jsonify(ret)


#告警上报(发包收包情况收集)
@app.route('/api/alarm/', methods=['POST'])
@app.route('/api/alarm', methods=['POST'])
def alarm_report():
    payload =  {}
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
    if not payload.get('data'):
        ret = {'status': -2, 'error': status_ret.get(-2)}
        return jsonify(ret)

    # TODO(smaug) varify token

    alarm_ip = request.headers.get('X-Forwarded-For') or request.headers.get('X-Real-IP') or request.remote_addr
    slog.info("recv alarm from ip:{0} size:{1}".format(alarm_ip, len(payload.get('data'))))
    mq.handle_alarm(payload.get('data'))
    ret = {'status': 0, 'error': status_ret.get(0)}
    return jsonify(ret)


def run():
    slog.info('proxy start...')
    slogging.start_log_monitor()
    app.run(host="127.0.0.1", port= 9091, debug=True)
    #app.run()
    return


if __name__ == '__main__':
    run()
