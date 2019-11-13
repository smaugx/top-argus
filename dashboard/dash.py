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
import threading

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/index', methods=['GET'])
@app.route('/index/', methods=['GET'])
def index():
    return 'Hello, World!'

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

    print("query hash: {0}".format(chain_hash))
    #TODO(smaug) get hash
    #packet_info = alarm_entity.get_chain_hash(chain_hash)
    packet_info = {}
    if not packet_info:
        ret = {'status': -1, 'error': status_ret.get(-1)}
        return jsonify(ret)
    ret = {'status':0,'error': status_ret.get(0), 'packet_info': packet_info}
    return jsonify(ret)


def run():
    app.run(host="0.0.0.0", port= 8080, debug=True)





if __name__ == '__main__':
    run()
