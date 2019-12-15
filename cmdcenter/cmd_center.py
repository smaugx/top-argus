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
import my_queue

app = Flask(__name__)

mycommand =  {}


@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/index', methods=['GET'])
@app.route('/index/', methods=['GET'])
def index():
    return 'Hello, World!'

# command get and update
@app.route('/api/command/', methods=['GET', 'PUT'])
@app.route('/api/command', methods=['GET', 'PUT'])
def command_update():
    status_ret = {
            0:'OK',
            -1:'权限验证失败',
            -2:'格式转化出错，请检查字段数或者字段格式等',
            -3: '不支持的方法',
            }
    ret = {}
    if request.method == 'GET':
        alarm_ip = request.remote_addr or request.X-Real-IP
        slog.info("update command ip:{0}".format(alarm_ip))
        ret = {'status': 0, 'error': status_ret.get(0), 'command': mycommand}
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
        
        command = payload.get('command') # list of command
        if not command:
            ret['status'] = -2
            ret['error'] = status_ret.get(-2)
            return jsonify(ret)

        if payload.get('test') == 'true':
            out = '[test] update command: {0} old_command'.format(json.dumps(command), json.dumps(mycommand, indent = 4))
            print(out)
            slog.info(out)
            ret['status'] = 0
            ret['error'] = status_ret.get(0)
            ret['command'] = command 
            return jsonify(ret)

        if payload.get('test') == 'false':
            now = int(time.time())
            for key in list(mycommand):
                if now - key >= 10 * 60:
                    mycommand.pop(key)

            out = 'update command: {0} old_command'.format(json.dumps(command), json.dumps(mycommand, indent = 4))
            print(out)
            slog.info(out)
            mycommand[now] = command
            slog.info('udpate command finished, command is: {0}'.format(json.dumps(mycommand, indent = 4)))
            ret['status'] = 0
            ret['error'] = status_ret.get(0)
            ret['command'] = command 
            return jsonify(ret)

    ret['status'] = -3
    ret['error'] = status_ret.get(-3)
    slog.info('not supported method:{0} of /api/command'.format(request.method))
    return jsonify(ret)



def run():
    app.run(host="0.0.0.0", port= 9091, debug=True)
    # app.run()


if __name__ == '__main__':
    run()
