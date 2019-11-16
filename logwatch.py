#!/usr/bin/env python3
#! -*- coding:utf8 -*-


import os
import queue
import time
import pdb
import requests
import json
import threading
import sys

#xnetwork-08:35:49.631-T1719:[Keyfo]-(elect_vhost.cc: HandleRumorMessage:381): original_elect_vhost_send local_node_id:010000fc609372cc194a437ae775bdbf00000000d60a7c10e9cc5f94e24cb9c63ee1fba3 chain_hash:3340835543 chain_msgid:655361 chain_msg_size:1382 send_timestamp:1573547735068 src_node_id:67000000ff7fff7fffffffffffffffff0000000032eae48d5405ad0a57173799f7490716 dest_node_id:67000000ff7fff7fffffffffffffffff0000000061d1343f82769c3eff69c5448e7b1fe5 is_root:0 broadcast:0

#xnetwork-08:35:49.631-T1719:[Keyfo]-(elect_vhost.cc: HandleRumorMessage:381): final_handle_rumor local_node_id:010000fc609372cc194a437ae775bdbf00000000d60a7c10e9cc5f94e24cb9c63ee1fba3 chain_hash:771962061 chain_msgid:655361 packet_size:608 chain_msg_size:196 hop_num:1 recv_timestamp:1573547749646 src_node_id:690000010140ff7fffffffffffffffff000000009aee88245d7e31e7abaab1ac9956d5a0 dest_node_id:690000010140ff7fffffffffffffffff0000000032eae48d5405ad0a57173799f7490716 is_root:0 broadcast:0

SENDQ = queue.Queue(10000)
RECVQ = queue.Queue(10000)
SAMP_RATE = 1  # sampling 10%

def clear_queue():
    global SENDQ, RECVQ
    while not SENDQ.empty():
        SENDQ.get()
    while not RECVQ.empty():
        RECVQ.get()
    print("clear sendqueue/recvqueue")

def print_queue():
    global SENDQ, RECVQ
    print("sendqueue.size = {0}, recvqueue.size = {1}".format(SENDQ.qsize(), RECVQ.qsize()))

def grep_log(line):
    global SENDQ, RECVQ
    try:
        #print('line: {0}'.format(line))
        send_flag = False if (line.find('alarm elect_vhost_original_send') == -1) else True
        recv_flag = False if (line.find('alarm elect_vhost_final_recv') == -1) else True
        if not send_flag and not recv_flag:
            return SENDQ.qsize(), RECVQ.qsize()

        
        packet_info = {}
        local_node_id_index  = line.find('local_node_id') 
        line = line[local_node_id_index:]
        sp_line = line.split()
        for item in sp_line:
            sp_item = item.split(':')
            key = sp_item[0]
            value = sp_item[1]
            packet_info[key] = value
        #print(packet_info)
        
        try:
            if send_flag:
                SENDQ.put(packet_info, block=True, timeout =2)
            if recv_flag:
                RECVQ.put(packet_info, block=True, timeout =2)
            print("grep_log ok")
        except Exception as e:
            print("queue full, drop packet_info")

    except Exception as e:
        print("grep_log exception: {0}".format(e))
        print(line)

    print_queue()
    return SENDQ.qsize(), RECVQ.qsize()

def watchlog(filename, offset = 0):
    try:
        #log_handle = open(filename, 'r',encoding="utf-8", errors='replace')
        log_handle = open(filename, 'r',encoding="utf-8")
    except Exception as e:
        print("open file exception: {0}".format(e))
        return offset

    wait_num = 0
    #log_handle.seek(0, 2)   # go to end
    log_handle.seek(offset, 0)   # go to offset from head
    cur_pos = log_handle.tell()
    print("1")
    while True:
        cur_pos = log_handle.tell()
        try:
            line = log_handle.readline()
        except Exception as e:
            print("readline exception:{0}, cur_pos:{1}".format(e, cur_pos))
            continue
        if not line:
            wait_num += 1
            log_handle.seek(cur_pos)  # go to cur_pos from head
            time.sleep(1)
            print("sleep 1 s, cur_pos: {0}".format(cur_pos))
            print_queue()
            if wait_num > 4:
                print("file: {0} done watch, size: {1}".format(filename, cur_pos))
                break
        else:
            send_size, recv_size = grep_log(line)
            wait_num = 0

    print("2")
    # judge new file "$filename" created
    if not os.path.exists(filename):
        return cur_pos
    try:
        new_log_handle = open(filename, 'r',encoding="utf-8")
    except Exception as e:
        return cur_pos

    new_log_handle.seek(0, 2)   # go to end
    new_size = new_log_handle.tell()
    if new_size >= cur_pos:
        return cur_pos

    # new file "$filename" created
    print("new file: {0} created".format(filename))
    return 0

def run_watch(filename = './xtop.log'):
    global SENDQ, RECVQ
    clear_queue()
    offset = 0
    while True:
        time.sleep(1)
        offset = watchlog(filename, offset)
        print("grep_log finish, sendq.size = {0} recvq.size = {1}, offset = {2}".format(SENDQ.qsize(), RECVQ.qsize(), offset))

def do_alarm(alarm_list):
    url = 'http://127.0.0.1:9090/api/alarm/'
    my_headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
            'Content-Type': 'application/json;charset=UTF-8',
            }
    my_data = json.dumps(alarm_list)
    try:
        res = requests.post(url, headers = my_headers,data = my_data, timeout = 5)
        if res.status_code == 200:
            if res.json().get('status') == 0:
                #slog.info("send alarm ok, response: {0}".format(res.text))
                print("send alarm ok, response: {0}".format(res.text))
            else:
                #slog.info("send alarm fail, response: {0}".format(res.text))
                print("send alarm fail, response: {0}".format(res.text))
        else:
            #slog.warn('send alarm fail: {0}'.format(res.text))
            print('send alarm fail: {0}'.format(res.text))
    except Exception as e:
        #slog.error("exception: {0}".format(e))
        print("exception: {0}".format(e))

    return



def consumer_send():
    global SENDQ, RECVQ, SAMP_RATE
    th_name = threading.current_thread().name
    alarm_list = []
    while True:
        try:
            time.sleep(1)
            while not SENDQ.empty():
                print("thread:{0} consumer_send size: {1}".format(th_name, SENDQ.qsize()))
                if len(alarm_list) >= 10:
                    print("send do_alarm")
                    do_alarm(alarm_list)
                    alarm_list.clear()

                packet_info = SENDQ.get()
                if int(packet_info.get('chain_hash')) % SAMP_RATE == 0:
                    alarm_list.append(packet_info)
        except Exception as e:
            pass

def consumer_recv():
    global SENDQ, RECVQ, SAMP_RATE
    th_name = threading.current_thread().name
    alarm_list = []
    while True:
        try:
            time.sleep(1)
            while not RECVQ.empty():
                print("thread:{0} consumer_recv size: {1}".format(th_name, RECVQ.qsize()))
                if len(alarm_list) >= 10:
                    print("recv do_alarm")
                    do_alarm(alarm_list)
                    alarm_list.clear()

                packet_info = RECVQ.get()
                if int(packet_info.get('chain_hash')) % SAMP_RATE == 0:
                    alarm_list.append(packet_info)
        except Exception as e:
            pass

def consumer_recv_test():
    global SENDQ, RECVQ
    alarm_list = []
    while True:
        try:
            time.sleep(1)
            while not RECVQ.empty():
                print("consumer_recv size: {0}".format(RECVQ.qsize()))
                if len(alarm_list) >= 10:
                    print("recv do_alarm")
                    do_alarm(alarm_list)
                    alarm_list.clear()

                packet_info = RECVQ.get()
                alarm_list.append(packet_info)
        except Exception as e:
            pass



    
if __name__ == "__main__":
    filename = './xtop.log'
    if len(sys.argv) == 2:
        filename = sys.argv[1]
    #run_watch(filename)

    watchlog_th = threading.Thread(target = run_watch, args = (filename, ))
    watchlog_th.start()
    print("start watchlog thread")

    con_send_th = threading.Thread(target = consumer_send)
    con_send_th.start()
    print("start consumer_send thread")


    con_recv_th = threading.Thread(target = consumer_recv)
    con_recv_th.start()
    print("start consumer_recv thread")

    con_recv_th2 = threading.Thread(target = consumer_recv)
    con_recv_th2.start()
    print("start consumer_recv2 thread")

    print('main thread wait...')
    watchlog_th.join()
    con_send_th.join()
    con_recv_th.join()
