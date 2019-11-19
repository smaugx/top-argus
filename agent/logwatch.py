#!/usr/bin/env python3
#! -*- coding:utf8 -*-

import os
now_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(now_dir)  #parent dir
activate_this = '%s/vvlinux/bin/activate_this.py' % base_dir
exec(open(activate_this).read())

import sys
sys.path.insert(0, base_dir)


import queue
import time
import pdb
import requests
import copy
import json
import threading
import operator
from common.slogging import slog

#xnetwork-08:35:49.631-T1719:[Keyfo]-(elect_vhost.cc: HandleRumorMessage:381): original_elect_vhost_send local_node_id:010000fc609372cc194a437ae775bdbf00000000d60a7c10e9cc5f94e24cb9c63ee1fba3 chain_hash:3340835543 chain_msgid:655361 chain_msg_size:1382 send_timestamp:1573547735068 src_node_id:67000000ff7fff7fffffffffffffffff0000000032eae48d5405ad0a57173799f7490716 dest_node_id:67000000ff7fff7fffffffffffffffff0000000061d1343f82769c3eff69c5448e7b1fe5 is_root:0 broadcast:0

#xnetwork-08:35:49.631-T1719:[Keyfo]-(elect_vhost.cc: HandleRumorMessage:381): final_handle_rumor local_node_id:010000fc609372cc194a437ae775bdbf00000000d60a7c10e9cc5f94e24cb9c63ee1fba3 chain_hash:771962061 chain_msgid:655361 packet_size:608 chain_msg_size:196 hop_num:1 recv_timestamp:1573547749646 src_node_id:690000010140ff7fffffffffffffffff000000009aee88245d7e31e7abaab1ac9956d5a0 dest_node_id:690000010140ff7fffffffffffffffff0000000032eae48d5405ad0a57173799f7490716 is_root:0 broadcast:0

SENDQ = queue.Queue(10000)
RECVQ = queue.Queue(10000)
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


def update_config_from_remote():
    global gconfig
    url = 'http://127.0.0.1:9090/api/config/'
    my_headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
            'Content-Type': 'application/json;charset=UTF-8',
            }
    config = {}
    try:
        res = requests.get(url, headers = my_headers, timeout = 5)
        if res.status_code == 200:
            if res.json().get('status') == 0:
                slog.info("get remote config ok, response: {0}".format(res.text))
                config = res.json().get('config')
    except Exception as e:
        slog.info("exception: {0}".format(e))
        return False

    if not config:
        slog.info("get remote config fail")
        return False
    # TODO(smaug) do something check for config
    if operator.eq(config, gconfig):
        slog.info('get remote config same as default')
        return True

    gconfig = copy.deepcopy(config)
    slog.info('get remote config ok: {0}'.format(json.dumps(gconfig)))
    return True

def clear_queue():
    global SENDQ, RECVQ
    while not SENDQ.empty():
        SENDQ.get()
    while not RECVQ.empty():
        RECVQ.get()
    slog.info("clear sendqueue/recvqueue")

def print_queue():
    global SENDQ, RECVQ
    slog.info("sendqueue.size = {0}, recvqueue.size = {1}".format(SENDQ.qsize(), RECVQ.qsize()))

def put_sendq(alarm_payload):
    global SENDQ
    try:
        SENDQ.put(alarm_payload, block=True, timeout =2)
        slog.info("put send_queue:{0} size:{1}, item:{2}".format(SENDQ, SENDQ.qsize(),json.dumps(alarm_payload)))
    except Exception as e:
        slog.info("queue full, drop alarm_payload")
        return False
    return True

def put_recvq(alarm_payload):
    global RECVQ 
    try:
        RECVQ.put(alarm_payload, block=True, timeout =2)
        slog.info("put recv_queue:{0} size:{1} item:{2}".format(RECVQ, RECVQ.qsize(),json.dumps(alarm_payload)))
    except Exception as e:
        slog.info("queue full, drop alarm_payload")
        return False
    return True
    
# grep broadcast log
def grep_log_broadcast(line):
    global SENDQ, RECVQ, gconfig
    grep_broadcast = gconfig.get('grep_broadcast')

    '''
    # something like: 
    'grep_broadcast': {
        'start': 'true',
        'sample_rate': 100,
        'network_focus_on': ['660000', '680000', '690000'], # src or dest
        'network_ignore':   ['670000'],  # src or dest
        }
    '''
    try:
        if grep_broadcast.get('start') != 'true':
            return False

        #slog.info('line: {0}'.format(line))
        send_flag = False if (line.find('alarm elect_vhost_original_send') == -1) else True
        recv_flag = False if (line.find('alarm elect_vhost_final_recv') == -1) else True
        if not send_flag and not recv_flag:
            return False

        if line.find('broadcast:1') == -1:
            slog.info('grep_broadcast found point2point')
            return False

        # do something filtering
        network_ignore = grep_broadcast.get('network_ignore')
        for ni in network_ignore:
            if line.find(ni) != -1:
                slog.info('grep_broadcast network_ignore {0}'.format(ni))
                return False
        network_focus_on = grep_broadcast.get('network_focus_on')
        nf_ret = False
        for nf in network_focus_on:
            if line.find(nf) != -1:
                nf_ret = True
                break
        if not nf_ret:
            slog.info('grep_broadcast network_focus_on get nothing')
            return False

        global_sample_rate = gconfig.get('global_sample_rate')
        sample_rate = grep_broadcast.get('sample_rate')
        if global_sample_rate < sample_rate:
            sample_rate = global_sample_rate
        rand_num = random.randint(0, 1000000)
        rn = rand_num % 100 + 1  # [0,100]
        if rn > sample_rate:
            slog.info('grep_broadcast final sample_rate:{0} rn:{1} return'.format(sample_rate, rn))
            return False
        slog.info('grep_broadcast final sample_rate:{0} rn:{1} go-on'.format(sample_rate, rn))

        packet_info = {}
        local_node_id_index  = line.find('local_node_id') 
        line = line[local_node_id_index:]
        sp_line = line.split()
        for item in sp_line:
            sp_item = item.split(':')
            key = sp_item[0]
            value = sp_item[1]
            packet_info[key] = value
        #slog.info(packet_info)
        alarm_payload = {
                'alarm_type': grep_broadcast.get('alarm_type'),
                'alarm_content': packet_info,
                }

        if send_flag:
            put_sendq(alarm_payload)
        if recv_flag:
            put_recvq(alarm_payload)

    except Exception as e:
        slog.info("grep_log exception: {0} line:{1}".format(e, line))
        return False
    return True

# grep point2point log
def grep_log_point2point(line):
    global SENDQ, RECVQ, gconfig
    grep_point2point = gconfig.get('grep_point2point')

    '''
    # something like: 
    'grep_point2point': {
        'start': 'false',
        'sample_rate': 100,
        'network_focus_on': ['660000', '680000', '690000'], # src or dest
        'network_ignore':   ['670000'],  # src or dest
        },
    '''
    try:
        if grep_point2point.get('start') != 'true':
            return False

        #slog.info('line: {0}'.format(line))
        send_flag = False if (line.find('alarm elect_vhost_original_send') == -1) else True
        recv_flag = False if (line.find('alarm elect_vhost_final_recv') == -1) else True
        if not send_flag and not recv_flag:
            return False

        if line.find('broadcast:0') == -1:
            slog.info('grep_point2point found broadcast')
            return False

        # do something filtering
        network_ignore = grep_point2point.get('network_ignore')
        for ni in network_ignore:
            if line.find(ni) != -1:
                slog.info('grep_point2point network_ignore {0}'.format(ni))
                return False
        network_focus_on = grep_point2point.get('network_focus_on')
        nf_ret = False
        for nf in network_focus_on:
            if line.find(nf) != -1:
                nf_ret = True
                break
        if not nf_ret:
            slog.info('grep_point2point network_focus_on get nothing')
            return False

        global_sample_rate = gconfig.get('global_sample_rate')
        sample_rate = grep_point2point.get('sample_rate')
        if global_sample_rate < sample_rate:
            sample_rate = global_sample_rate
        rand_num = random.randint(0, 1000000)
        rn = rand_num % 100 + 1  # [0,100]
        if rn > sample_rate:
            slog.info('grep_point2point final sample_rate:{0} rn:{1} return'.format(sample_rate, rn))
            return False
        slog.info('grep_point2point final sample_rate:{0} rn:{1} go-on'.format(sample_rate, rn))

        packet_info = {}
        local_node_id_index  = line.find('local_node_id') 
        line = line[local_node_id_index:]
        sp_line = line.split()
        for item in sp_line:
            sp_item = item.split(':')
            key = sp_item[0]
            value = sp_item[1]
            packet_info[key] = value
        #slog.info(packet_info)

        alarm_payload = {
                'alarm_type': grep_broadcast.get('alarm_type'),
                'alarm_content': packet_info,
                }
        if send_flag:
            put_sendq(alarm_payload)
        if recv_flag:
            put_recvq(alarm_payload)

    except Exception as e:
        slog.info("grep_log exception: {0} line:{1}".format(e, line))
        return False
    return True


def grep_log(line):
    grep_log_broadcast(line)
    grep_log_point2point(line)

    print_queue()
    return SENDQ.qsize(), RECVQ.qsize()

def watchlog(filename, offset = 0):
    try:
        #log_handle = open(filename, 'r',encoding="utf-8", errors='replace')
        #log_handle = open(filename, 'r',encoding="utf-8")
        log_handle = open(filename, 'r',encoding="latin-1")
    except Exception as e:
        slog.info("open file exception: {0}".format(e))
        return offset

    wait_num = 0
    #log_handle.seek(0, 2)   # go to end
    log_handle.seek(offset, 0)   # go to offset from head
    cur_pos = log_handle.tell()
    while True:
        cur_pos = log_handle.tell()
        try:
            line = log_handle.readline()
        except Exception as e:
            slog.info("readline exception:{0}, cur_pos:{1}".format(e, cur_pos))
            continue
        if not line:
            wait_num += 1
            log_handle.seek(cur_pos)  # go to cur_pos from head
            time.sleep(1)
            slog.info("sleep 1 s, cur_pos: {0}".format(cur_pos))
            print_queue()
            if wait_num > 4:
                slog.info("file: {0} done watch, size: {1}".format(filename, cur_pos))
                break
        else:
            send_size, recv_size = grep_log(line)
            wait_num = 0

    # judge new file "$filename" created
    if not os.path.exists(filename):
        return cur_pos
    try:
        new_log_handle = open(filename, 'r',encoding="latin-1")
    except Exception as e:
        return cur_pos

    new_log_handle.seek(0, 2)   # go to end
    new_size = new_log_handle.tell()
    if new_size >= cur_pos:
        return cur_pos

    # new file "$filename" created
    slog.info("new file: {0} created".format(filename))
    return 0

def run_watch(filename = './xtop.log'):
    global SENDQ, RECVQ
    clear_queue()
    offset = 0
    while True:
        time.sleep(1)
        offset = watchlog(filename, offset)
        slog.info("grep_log finish, sendq.size = {0} recvq.size = {1}, offset = {2}".format(SENDQ.qsize(), RECVQ.qsize(), offset))

def do_alarm(alarm_list):
    url = 'http://127.0.0.1:9090/api/alarm/'
    my_headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
            'Content-Type': 'application/json;charset=UTF-8',
            }
    my_data = json.dumps(alarm_list)
    slog.info("do_alarm: {0}".format(my_data))
    try:
        res = requests.post(url, headers = my_headers,data = my_data, timeout = 5)
        if res.status_code == 200:
            if res.json().get('status') == 0:
                slog.info("send alarm ok, response: {0}".format(res.text))
            else:
                slog.info("send alarm fail, response: {0}".format(res.text))
        else:
            slog.info('send alarm fail: {0}'.format(res.text))
    except Exception as e:
        slog.info("exception: {0}".format(e))

    return



def consumer_send():
    global SENDQ, RECVQ, gconfig
    alarm_pack_num = gconfig.get('alarm_pack_num')
    th_name = threading.current_thread().name
    alarm_list = []
    while True:
        try:
            slog.info("consumer thread:{0} send_queue:{1} size:{2}".format(th_name, SENDQ, SENDQ.qsize()))
            while not SENDQ.empty():
                alarm_payload = SENDQ.get()
                alarm_list.append(alarm_payload)

                if len(alarm_list) >= alarm_pack_num:
                    slog.info("send do_alarm")
                    do_alarm(alarm_list)
                    alarm_list.clear()

            time.sleep(1)
        except Exception as e:
            pass

def consumer_recv():
    global SENDQ, RECVQ, gconfig
    th_name = threading.current_thread().name
    alarm_pack_num = gconfig.get('alarm_pack_num')
    alarm_list = []
    while True:
        try:
            slog.info("consumer thread:{0} recv_queue:{1} size:{2}".format(th_name, RECVQ, RECVQ.qsize()))
            while not RECVQ.empty():
                alarm_payload = RECVQ.get()
                alarm_list.append(alarm_payload)

                if len(alarm_list) >= alarm_pack_num:
                    slog.info("recv do_alarm")
                    do_alarm(alarm_list)
                    alarm_list.clear()

            time.sleep(1)
        except Exception as e:
            pass

def consumer_recv_test():
    global SENDQ, RECVQ
    alarm_list = []
    while True:
        try:
            time.sleep(1)
            while not RECVQ.empty():
                slog.info("consumer_recv size: {0}".format(RECVQ.qsize()))
                if len(alarm_list) >= 10:
                    slog.info("recv do_alarm")
                    do_alarm(alarm_list)
                    alarm_list.clear()

                alarm_payload = RECVQ.get()
                alarm_list.append(alarm_payload)
        except Exception as e:
            pass



    
if __name__ == "__main__":
    if not update_config_from_remote():
        slog.error('using default config to start: {0}'.format(json.dumps(gconfig)))

    filename = './xtop.log'
    filename = gconfig.get('watch_filename')
    if len(sys.argv) == 2:
        filename = sys.argv[1]

    #run_watch(filename)

    watchlog_th = threading.Thread(target = run_watch, args = (filename, ))
    watchlog_th.start()
    slog.info("start watchlog thread")

    con_send_th = threading.Thread(target = consumer_send)
    con_send_th.start()
    slog.info("start consumer_send thread")


    con_recv_th = threading.Thread(target = consumer_recv)
    con_recv_th.start()
    slog.info("start consumer_recv thread")

    #con_recv_th2 = threading.Thread(target = consumer_recv)
    #con_recv_th2.start()
    #slog.info("start consumer_recv2 thread")

    slog.info('main thread wait...')
    watchlog_th.join()
    con_send_th.join()
    con_recv_th.join()
