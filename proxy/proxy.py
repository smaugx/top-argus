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
import copy
from common.slogging import slog
import my_queue

app = Flask(__name__)
#mq = my_queue.CacheQueue()
mq = my_queue.RedisQueue(host='127.0.0.1', port=6379, password='')
gconfig_shm_file = '/dev/shm/topargus_gconfig'

gconfig = {
        'global_sample_rate': 100,  # sample_rate%
        'alarm_pack_num': 2,   # upload alarm size one time
        'grep_broadcast': {
            'start': 'true',
            'sample_rate': 100,
            'alarm_type': 'packet',
            'network_focus_on': ['660000', '680000', '690000', '670000'], # src or dest
            'network_ignore':   ['650000'],  # src or dest
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
            'sample_rate': 20,
            'alarm_type': 'networksize',
            'network_focus_on': ['660000', '680000', '690000'], # src or dest
            'network_ignore':   ['670000'],  # src or dest
            },
        'grep_xtopchain': {
            'start': 'true',
            'alarm_type': 'progress',
            },
        }

def dump_gconfig():
    global gconfig, gconfig_shm_file
    with open(gconfig_shm_file,'w') as fout:
        fout.write(json.dumps(gconfig))
        fout.close()
    return

def load_gconfig():
    global gconfig, gconfig_shm_file
    with open(gconfig_shm_file,'r') as fin:
        gconfig = json.loads(fin.read())
        fin.close()
    return

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
    global gconfig
    status_ret = {
            0:'OK',
            -1:'权限验证失败',
            -2:'格式转化出错，请检查字段数或者字段格式等',
            -3: '不支持的方法',
            }
    ret = {}
    if request.method == 'GET':
        alarm_ip = request.remote_addr or request.headers.get('X-Real-IP')
        slog.info("update config ip:{0}".format(alarm_ip))
        gconfig = load_gconfig()
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

    alarm_ip = request.remote_addr or request.headers.get('X-Real-IP')
    slog.info("recv alarm from ip:{0} size:{1}".format(alarm_ip, len(payload.get('data'))))
    mq.handle_alarm(payload.get('data'))
    ret = {'status': 0, 'error': status_ret.get(0)}
    return jsonify(ret)


def run():
    slog.info('proxy start...')
    app.run(host="0.0.0.0", port= 9090, debug=True)
    #app.run()
    return


if __name__ == '__main__':
    run()
