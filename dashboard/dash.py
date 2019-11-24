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
import threading
import dash_core

app = Flask(__name__)

mydash = dash_core.Dash()


@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/index', methods=['GET'])
@app.route('/index/', methods=['GET'])
def index():
    return 'Hello, World!'

@app.route('/api/web/hash/<chain_hash>/', methods = ['GET'])
@app.route('/api/web/hash/<chain_hash>', methods = ['GET'])
def chain_hash_query(chain_hash):
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

    slog.debug("query hash: {0}".format(chain_hash))
    data = {'chain_hash': chain_hash}
    results,total = mydash.get_packet_info(data)
    if not results:
        ret = {'status': -1, 'error': status_ret.get(-1)}
        return jsonify(ret)
    ret = {'status':0,'error': status_ret.get(0), 'results': results}
    return jsonify(ret)

# GET /api/web/packet/?chain_hash=8180269&chain_msgid=393217&is_root=0&broadcast=1&send_node_id=010000&src_node_id=660000&dest_node_id=680000
@app.route('/api/web/packet/', methods = ['GET'])
@app.route('/api/web/packet', methods = ['GET'])
def packet_query():
    chain_hash   = request.args.get('chain_hash')       or None
    chain_msgid  = request.args.get('chain_msgid')      or None
    is_root      = request.args.get('is_root')          or None
    broadcast    = request.args.get('broadcast')        or None
    send_node_id = request.args.get('send_node_id')     or None
    src_node_id  = request.args.get('src_node_id')      or None
    dest_node_id = request.args.get('dest_node_id')     or None

    status_ret = {
            0:'OK',
            -1:'没有数据',
            }

    
    data = {
            'chain_hash': chain_hash,
            'chain_msgid': chain_msgid,
            'is_root': is_root,
            'broadcast': broadcast,
            'send_node_id': send_node_id,
            'src_node_id': src_node_id,
            'dest_node_id': dest_node_id,
            }
    results,total = mydash.get_packet_info(data)
    if results:
        ret = {'status':0,'error': status_ret.get(0) , 'results': results}
        return jsonify(ret)
    else:
        ret = {'status': -1,'error': status_ret.get(-1) , 'results': results}
        return jsonify(ret)
 
# GET /api/web/packet_recv/?chain_hash=8180269&recv_node_id=01000&recv_node_ip=127.0.0.1
@app.route('/api/web/packet_recv/', methods = ['GET'])
@app.route('/api/web/packet_recv', methods = ['GET'])
def packet_recv_query():
    chain_hash   = request.args.get('chain_hash')       or None
    recv_node_id = request.args.get('recv_node_id')     or None
    recv_node_ip = request.args.get('recv_node_ip')     or None

    status_ret = {
            0:'OK',
            -1:'没有数据',
            }

    data = {
            'chain_hash': chain_hash,
            'recv_node_id': recv_node_id,
            'recv_node_ip': recv_node_ip,
            }
    results,total = mydash.get_packet_recv_info(data)
    if results:
        ret = {'status':0,'error': status_ret.get(0) , 'results': results}
        return jsonify(ret)
    else:
        ret = {'status': -1,'error': status_ret.get(-1) , 'results': results}
        return jsonify(ret)
 




def run():
    app.run(host="0.0.0.0", port= 8080, debug=True)





if __name__ == '__main__':
    run()
