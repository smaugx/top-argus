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
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import sys
import json
import requests
import redis
import uuid
import time
import random
import base64
import copy
import threading
import dash_core
import dash_user
from common.slogging import slog

app = Flask(__name__)
auth = HTTPBasicAuth()

user_info = {
    'smaug1': generate_password_hash('hello1'),
    'smaug2': generate_password_hash('hello2')
    }

mydash = dash_core.Dash()
myuser = dash_user.User()

@auth.verify_password
def verify_password(username, password):
    global user_info
    print('username:{0}'.format(username))
    if username not in user_info:
        tmp_user_info = myuser.get_user_info()
        if tmp_user_info:
            slog.info('update user_info from db:{0}'.format(json.dumps(tmp_user_info)))
            for item in tmp_user_info:
                if item.get('username') not in user_info:
                    user_info[item.get('username')] = item.get('password_hash')
        else:
            slog.info('update user_info from db failed')

    if username not in user_info:
        return False
    if not check_password_hash(user_info.get(username), password):
        tmp_user_info = myuser.get_user_info()
        if not tmp_user_info:
            return False
        slog.info('update user_info from db:{0}'.format(json.dumps(tmp_user_info)))
        for item in tmp_user_info:
            if item.get('username') != username:
                continue
            user_info[username] = item.get('password_hash')

    return check_password_hash(user_info.get(username), password)


@app.route('/')
@auth.login_required
def hello_world():
    return '{0} Hello, World!'.format(auth.username())

@app.route('/index', methods=['GET'])
@app.route('/index/', methods=['GET'])
@auth.login_required
def index():
    return 'Hello, World!'

# GET /api/web/packet/?uniq_chain_hash=73439849340238&chain_hash=8180269&chain_msgid=393217&is_root=0&broadcast=1&send_node_id=010000&src_node_id=660000&dest_node_id=680000
@app.route('/api/web/packet/', methods = ['GET'])
@app.route('/api/web/packet', methods = ['GET'])
@auth.login_required
def packet_query():
    uniq_chain_hash   = request.args.get('uniq_chain_hash')       or None
    chain_hash        = request.args.get('chain_hash')            or None
    chain_msgid       = request.args.get('chain_msgid')           or None
    is_root           = request.args.get('is_root')               or None
    broadcast         = request.args.get('broadcast')             or None
    send_node_id      = request.args.get('send_node_id')          or None
    src_node_id       = request.args.get('src_node_id')           or None
    dest_node_id      = request.args.get('dest_node_id')          or None
    limit             = request.args.get('limit')                 or 200
    page              = request.args.get('page')                  or 1


    status_ret = {
            0:'OK',
            -1:'没有数据',
            -2: '参数不合法',
            }

    try:
        if uniq_chain_hash:
            uniq_chain_hash = int(uniq_chain_hash)
        if chain_hash:
            chain_hash = int(chain_hash)
        if chain_msgid:
            chain_msgid = int(chain_msgid)
        if limit != None:
            limit = int(limit)
        if page != None:
            page = int(page)
    except Exception as e:
        slog.warn("catch exception:{0}".format(e))
        ret = {'status': -2,'error': status_ret.get(-2) , 'results': []}
        return jsonify(ret)

    
    data = {
            'uniq_chain_hash': uniq_chain_hash,
            'chain_hash': chain_hash,
            'chain_msgid': chain_msgid,
            'is_root': is_root,
            'broadcast': broadcast,
            'send_node_id': send_node_id,
            'src_node_id': src_node_id,
            'dest_node_id': dest_node_id,
            }
    results,total = mydash.get_packet_info(data, limit, page)
    if results:
        ret = {'status':0,'error': status_ret.get(0) , 'results': results, 'total': total}
        return jsonify(ret)
    else:
        ret = {'status': -1,'error': status_ret.get(-1) , 'results': results, 'total': total}
        return jsonify(ret)
 
# GET /api/web/packet_recv/?uniq_chain_hash=4738749342390842903&chain_hash=8180269&recv_node_id=01000&recv_node_ip=127.0.0.1
@app.route('/api/web/packet_recv/', methods = ['GET'])
@app.route('/api/web/packet_recv', methods = ['GET'])
@auth.login_required
def packet_recv_query():
    uniq_chain_hash   = request.args.get('uniq_chain_hash')       or None
    chain_hash        = request.args.get('chain_hash')            or None
    recv_node_id      = request.args.get('recv_node_id')          or None
    recv_node_ip      = request.args.get('recv_node_ip')          or None
    limit             = request.args.get('limit')                 or None
    page              = request.args.get('page')                  or None

    if uniq_chain_hash:
        uniq_chain_hash = int(uniq_chain_hash)

    if chain_hash:
        chain_hash = int(chain_hash)

    status_ret = {
            0:'OK',
            -1:'没有数据',
            }

    data = {
            'uniq_chain_hash': uniq_chain_hash,
            'chain_hash': chain_hash,
            'recv_node_id': recv_node_id,
            'recv_node_ip': recv_node_ip,
            }
    results,total = mydash.get_packet_recv_info(data, limit, page)
    if results:
        ret = {'status':0,'error': status_ret.get(0) , 'results': results, 'total': total}
        return jsonify(ret)
    else:
        ret = {'status': -1,'error': status_ret.get(-1) , 'results': results, 'total': total}
        return jsonify(ret)
 
# GET /api/web/network/?onlysize=[true/false]&withip=[true/false]
# GET /api/web/network/?network_id=0100&onlysize=true/false&withip=[true/false]
# GET /api/web/network/?node_id=690000010140ff7fffffffffffffffff000000009aee88245d7e31e7abaab1ac9956d5a0&onlysize=true/false
# GET /api/web/network/?node_ip=127.0.0.1&onlysize=true/false
@app.route('/api/web/network/', methods = ['GET'])
@app.route('/api/web/network', methods = ['GET'])
@auth.login_required
def network_query():
    network_id = request.args.get('network_id')       or '010000'
    node_id    = request.args.get('node_id')          or None
    node_ip    = request.args.get('node_ip')          or None
    onlysize   = request.args.get('onlysize')         or None
    withip     = request.args.get('withip')           or None

    if onlysize == 'true':
        onlysize = True
    else:
        onlysize = False

    if withip == 'true':
        withip = True
    else:
        withip = False

    print(onlysize)
    status_ret = {
            0:'OK',
            -1:'没有数据',
            -2: '参数不合法',
            }

    data = {
            'network_id': network_id,
            'node_id': node_id,
            'node_ip': node_ip,
            'onlysize': onlysize,
            'withip': withip
            }

    history_max_node_size = 0
    if network_id.startswith('0100'):  # get real node
        ndata = {
                'simple': 'true',
                }
        node_info_results = mydash.get_node_info(ndata)
        if node_info_results.get('node_size'):
            history_max_node_size = node_info_results.get('node_size')
            slog.debug('get history_max_node_size:{0} for network_id:{1}'.format(history_max_node_size, network_id))

    results = mydash.get_network_ids_exp(data)
    if results:
        results['max_node_size'] = history_max_node_size
        ret = {'status':0,'error': status_ret.get(0) , 'results': results}
        return jsonify(ret)
    else:
        ret = {'status': -1,'error': status_ret.get(-1) , 'results': results}
        return jsonify(ret)
 
# GET /api/web/networkid/?virtual=true/false
@app.route('/api/web/networkid/', methods = ['GET'])
@app.route('/api/web/networkid', methods = ['GET'])
@auth.login_required
def networkid_query():
    virtual = request.args.get('virtual')         or None
    if virtual == 'false':
        virtual = False 
    else:
        virtual = True

    status_ret = {
            0:'OK',
            -1:'没有数据',
            -2: '参数不合法',
            }

    results = mydash.get_network_ids_list(virtual)
    if results:
        ret = {'status':0,'error': status_ret.get(0) , 'results': results}
        return jsonify(ret)
    else:
        ret = {'status': -1,'error': status_ret.get(-1) , 'results': results}
        return jsonify(ret)

# GET /api/web/packet_drop/?dest_node_id=680000&begin=1508954899&end=15089584959
@app.route('/api/web/packet_drop/', methods = ['GET'])
@app.route('/api/web/packet_drop', methods = ['GET'])
@auth.login_required
def packet_drop_query():
    now = int(time.time() * 1000)
    latest_hour = now - 24 * 60 * 60 * 1000 # 24 hour
    dest_node_id = request.args.get('dest_node_id')     or None
    begin        = request.args.get('begin')            or latest_hour
    end          = request.args.get('end')              or  now

    try:
        begin = int(begin)
        end = int(end)
        if begin >= end or (end - begin >= 24 * 60 * 60 * 1000 ):
            begin = end - 24 * 60 * 60 * 1000
        if end > now or (now - end  > 10 * 24 * 60 * 60 * 1000):
            end = now
            begin = latest_hour
    except Exception as e:
        begin = latest_hour
        end = now

    status_ret = {
            0:'OK',
            -1:'没有数据',
            }
    
    data = {
            'dest_node_id': dest_node_id,
            'begin': begin,
            'end': end
            }
    results = mydash.get_packet_drop(data)

    '''
    results = []
    tmp_time = now
    for i in range(0,60):
        tmp_time = tmp_time - (60 - i -1) * 60 * 1000
        results.append([tmp_time, random.randint(0,1000)])
    '''

    if results:
        ret = {'status':0,'error': status_ret.get(0) , 'results': results}
        return jsonify(ret)
    else:
        ret = {'status': -1,'error': status_ret.get(-1) , 'results': results}
        return jsonify(ret)


# GET /api/web/node_info/?simple=true&public_ip_port=127.0.0.1:9000&root=0100&status=online&rec=6400&zec=6500&edg=6600&arc=6700&adv=6800&val=6900
@app.route('/api/web/node_info/', methods = ['GET'])
@app.route('/api/web/node_info', methods = ['GET'])
@auth.login_required
def node_info_query():
    simple           = request.args.get('simple')            or 'false'
    public_ip_port   = request.args.get('public_ip_port')    or None
    root             = request.args.get('root')              or None
    status           = request.args.get('status')            or None
    rec              = request.args.get('rec')               or None 
    zec              = request.args.get('zec')               or None
    edg              = request.args.get('edg')               or None
    arc              = request.args.get('arc')               or None
    adv              = request.args.get('adv')               or None
    val              = request.args.get('val')               or None     

    status_ret = {
            0:'OK',
            -1:'没有数据',
            -2: '参数不合法',
            }

    data = {
            'simple':           simple,
            'public_ip_port':   public_ip_port,
            'root':             root,
            'status':           status,
            'rec':              rec,
            'zec':              zec,
            'edg':              edg,
            'arc':              arc,
            'adv':              adv,
            'val':              val,
    }

    results = mydash.get_node_info(data)
    if results:
        ret = {'status':0,'error': status_ret.get(0) , 'results': results}
        return jsonify(ret)
    else:
        ret = {'status': -1,'error': status_ret.get(-1) , 'results': results}
        return jsonify(ret)




def run():
    app.run(host="0.0.0.0", port= 8080, debug=True)
    #app.run()

if __name__ == '__main__':
    run()
