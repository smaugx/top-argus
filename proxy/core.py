#!/usr/bin/env python
#-*- coding:utf8 -*-


import json
import time
import queue


#{"local_node_id": "010000fc609372cc194a437ae775bdbf00000000d60a7c10e9cc5f94e24cb9c63ee1fba3", "chain_hash": "4165143189", "chain_msgid": "655361", "chain_msg_size": "9184", "send_timestamp": "1573547749649", "src_node_id": "690000010140ff7fffffffffffffffff0000000032eae48d5405ad0a57173799f7490716", "dest_node_id": "690000010140ff7fffffffffffffffff000000009aee88245d7e31e7abaab1ac9956d5a0", "is_root": "0", "broadcast": "0"}

#{"local_node_id": "010000fc609372cc194a437ae775bdbf00000000d60a7c10e9cc5f94e24cb9c63ee1fba3", "chain_hash": "1146587997", "chain_msgid": "917505", "packet_size": "602", "chain_msg_size": "189", "hop_num": "1", "recv_timestamp": "1573547749394", "src_node_id": "010000ffffffffffffffffffffffffff0000000088ae064b2bb22948a2aee8ecd81c08f9", "dest_node_id": "67000000ff7fff7fffffffffffffffff0000000032eae48d5405ad0a57173799f7490716", "is_root": "0", "broadcast": "0"}

PACKET_INFO_CACHE = {}
ALARM_QUEUE = queue.Queue(10000)

def handle_alarm(alarm_list):
    global ALARM_QUEUE
    if not alarm_list:
        return

    for item in alarm_list:
        ALARM_QUEUE.put(item, block=True, timeout = 2)
    print("put {0} alarm in queue, now size is {1}".format(len(alarm_list), ALARM_QUEUE.qsize()))
    return

def consume_alarm():
    global ALARM_QUEUE, PACKET_INFO_CACHE
    while True:
        time.sleep(1)
        try:
            while not ALARM_QUEUE.empty():
                packet_info = ALARM_QUEUE.get()
                chain_hash = int(packet_info.get('chain_hash'))
                if not packet_info.get('send_timestamp'):
                    if not PACKET_INFO_CACHE.get(chain_hash):
                        # this is recv info,and befor send info
                        ALARM_QUEUE.put(packet_info, block=True, timeout=2)
                        continue
                    else: #recv info and after send info
                        cache_packet_info = PACKET_INFO_CACHE.get(chain_hash)
                        cache_packet_info['recv_nodes_id'].append(packet_info.get('local_node_id'))
                        cache_packet_info['packet_size'] = (cache_packet_info.get('packet_size') * cache_packet_info.get('recv_nodes_num') + int(packet_info.get('packet_size'))) / (cache_packet_info.get('recv_nodes_num') + 1)
                        cache_packet_info['recv_nodes_num'] += 1
                        hop_num  = int(packet_info.get('hop_num'))
                        if hop_num < 5:
                            cache_packet_info['hop_num']['0_5'] += 1
                        elif 5 <= hop_num and hop_num < 10:
                            cache_packet_info['hop_num']['5_10'] += 1
                        elif 10 <= hop_num and hop_num < 15:
                            cache_packet_info['hop_num']['10_15'] += 1
                        elif 15 <= hop_num and hop_num < 20:
                            cache_packet_info['hop_num']['15_20'] += 1
                        else:
                            cache_packet_info['hop_num']['20_'] += 1
                        recv_timestamp = int(packet_info.get('recv_timestamp'))
                        send_timestamp = cache_packet_info.get('send_timestamp')
                        taking = recv_timestamp - send_timestamp    # ms
                        if taking < 500:
                            cache_packet_info['taking']['0.0_0.5'] += 1
                        elif 500 <= taking and taking < 1000:
                            cache_packet_info['taking']['0.5_1.0'] += 1
                        elif 1000 <= taking and taking < 1500:
                            cache_packet_info['taking']['1.0_1.5'] += 1
                        elif 1500 <= taking and taking < 2000:
                            cache_packet_info['taking']['1.5_2.0'] += 1
                        else:
                            cache_packet_info['taking']['2.0_'] += 1

                        # update packet_info
                        print("update packet_info: {0}".format(json.dumps(cache_packet_info)))
                        PACKET_INFO_CACHE[chain_hash] = cache_packet_info

                else:  # this is send info
                    cache_packet_info = {}
                    cache_packet_info['send_node_id'] = packet_info.get('local_node_id')
                    cache_packet_info['chain_hash'] = int(packet_info.get('chain_hash'))
                    cache_packet_info['chain_msgid'] = int(packet_info.get('chain_msgid'))
                    cache_packet_info['chain_msg_size'] = int(packet_info.get('chain_msg_size'))
                    cache_packet_info['send_timestamp'] = int(packet_info.get('send_timestamp'))
                    cache_packet_info['src_node_id'] = packet_info.get('src_node_id')
                    cache_packet_info['dest_node_id'] = packet_info.get('dest_node_id')
                    cache_packet_info['is_root'] = int(packet_info.get('is_root'))
                    cache_packet_info['broadcast'] = int(packet_info.get('broadcast'))
                    cache_packet_info['recv_nodes_id'] = []
                    cache_packet_info['packet_size'] = 0
                    cache_packet_info['recv_nodes_num'] = 0
                    cache_packet_info['hop_num'] = {
                            '0_5':0,
                            '5_10':0,
                            '10_15':0,
                            '20_':0
                            }
                    cache_packet_info['taking'] = {
                            '0.0_0.5':0,
                            '0.5_1.0':0,
                            '1.0_1.5':0,
                            '1.5_2.0':0,
                            '2.0_':0
                            }
                    # insert to cache
                    print("insert packet_info: {0}".format(json.dumps(cache_packet_info)))
                    PACKET_INFO_CACHE[chain_hash] = cache_packet_info
        except Exception as e:
            print('consumer catch exception: {0}'.format(e))
    return



