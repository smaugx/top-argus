#!/usr/bin/env python3
#! -*- coding:utf8 -*-


import os
import queue
import time
import pdb

#original_elect_vhost_send local_node_id:010000fc609372cc194a437ae775bdbf00000000d60a7c10e9cc5f94e24cb9c63ee1fba3 chain_hash:3340835543 chain_msgid:655361 chain_msg_size:1382 send_timestamp:1573547735068 src_node_id:67000000ff7fff7fffffffffffffffff0000000032eae48d5405ad0a57173799f7490716 dest_node_id:67000000ff7fff7fffffffffffffffff0000000061d1343f82769c3eff69c5448e7b1fe5 is_root:0 broadcast:0

#xnetwork-08:35:49.631-T1719:[Keyfo]-(elect_vhost.cc: HandleRumorMessage:381): final_handle_rumor local_node_id:010000fc609372cc194a437ae775bdbf00000000d60a7c10e9cc5f94e24cb9c63ee1fba3 chain_hash:771962061 chain_msgid:655361 packet_size:608 chain_msg_size:196 hop_num:1 recv_timestamp:1573547749646 src_node_id:690000010140ff7fffffffffffffffff000000009aee88245d7e31e7abaab1ac9956d5a0 dest_node_id:690000010140ff7fffffffffffffffff0000000032eae48d5405ad0a57173799f7490716 is_root:0 broadcast:0

SENDQ = queue.Queue(10000)
RECVQ = queue.Queue(10000)

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
        send_flag = False if (line.find('original_elect_vhost') == -1) else True
        recv_flag = False if (line.find('final_handle_rumor') == -1) else True
        if not send_flag and not recv_flag:
            return SENDQ.qsize(), RECVQ.qsize()

        #print('line {0} : {1}'.format(line_num, line))
        
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
        
        if send_flag:
            SENDQ.put(packet_info, block=True, timeout =2)
        if recv_flag:
            RECVQ.put(packet_info, block=True, timeout =2)
        print("grep_log ok")
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
    while True:
        cur_pos = log_handle.tell()
        try:
            line = log_handle.readline()
        except Exception:
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

def run_watch():
    global SENDQ, RECVQ
    clear_queue()
    filename = './xtop.log'
    offset = 0
    while True:
        time.sleep(1)
        offset = watchlog(filename, offset)
        print("grep_log finish, sendq.size = {0} recvq.size = {1}".format(SENDQ.qsize(), RECVQ.qsize()))
    
if __name__ == "__main__":
    run_watch()
