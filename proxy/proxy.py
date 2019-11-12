#!/usr/bin/env python
#-*- coding:utf8 -*-

import os 
now_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(now_dir)  #parent dir
activate_this = '%s/vv/bin/activate_this.py' % base_dir
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

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!'

#告警上报
@app.route('/api/alarm/', methods=['POST'])
@app.route('/api/alarm', methods=['POST'])
def alarm_report():
    if not request.is_json:
        payload = json.loads(request.data)
    else:
        payload = request.get_json()

    ret = {'status':''}
    status_ret = {
            0:'OK',
            -1:'上报字段不合法,部分可能上传失败',
            -2:'不存在此服务项,部分可能上传失败',
            -3:'格式转化出错，请检查字段数或者字段格式等'
            }

    print("recv alarm: {0}".format(json.dumps(payload)))
    ret = {'status': 0}
    return jsonify(ret)

