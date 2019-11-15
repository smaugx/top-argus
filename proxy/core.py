#!/usr/bin/env python
#-*- coding:utf8 -*-


import json
import time
import queue
import copy
import threading


#{"local_node_id": "010000fc609372cc194a437ae775bdbf00000000d60a7c10e9cc5f94e24cb9c63ee1fba3", "chain_hash": "4165143189", "chain_msgid": "655361", "chain_msg_size": "9184", "send_timestamp": "1573547749649", "src_node_id": "690000010140ff7fffffffffffffffff0000000032eae48d5405ad0a57173799f7490716", "dest_node_id": "690000010140ff7fffffffffffffffff000000009aee88245d7e31e7abaab1ac9956d5a0", "is_root": "0", "broadcast": "0"}

#{"local_node_id": "010000fc609372cc194a437ae775bdbf00000000d60a7c10e9cc5f94e24cb9c63ee1fba3", "chain_hash": "1146587997", "chain_msgid": "917505", "packet_size": "602", "chain_msg_size": "189", "hop_num": "1", "recv_timestamp": "1573547749394", "src_node_id": "010000ffffffffffffffffffffffffff0000000088ae064b2bb22948a2aee8ecd81c08f9", "dest_node_id": "67000000ff7fff7fffffffffffffffff0000000032eae48d5405ad0a57173799f7490716", "is_root": "0", "broadcast": "0"}

class Alarm(object):
    def __init__(self):
        self.packet_info_lock_ = threading.Lock()
        # key is chain_hash, value is packet_info
        self.packet_info_cache_ = {}
        # keep the order of insert
        self.packet_info_chain_hash_ = []
        
        # store packet_info from /api/alarm
        self.alarm_queue_ = queue.Queue(10000) 
        
        #template of packet_info
        self.template_packet_info_ = {
                'chain_hash': 0,
                'chain_msgid': 0,
                'chain_msg_size': 0,
                'packet_size': 0,
                'send_timestamp': 0,
                'is_root': 0,
                'broadcast': 1,
                'send_node_id': '',
                'src_node_id': '',
                'dest_node_id': '',
                'recv_nodes_id': [],   # HexSubstr
                'recv_nodes_ip': [],   # nodeip
                'recv_nodes_num': 0,
                'hop_num': {
                '0_5':0,
                '5_10':0,
                '10_15':0,
                '20_':0
                },
                'taking': {
                '0.0_0.5':0,
                '0.5_1.0':0,
                '1.0_1.5':0,
                '1.5_2.0':0,
                '2.0_':0
                },
            }
        

    # handle alarm 
    def handle_alarm(self, alarm_list):
        if not alarm_list:
            return
    
        for item in alarm_list:
            self.alarm_queue_.put(item, block=True, timeout = 2)
        print("put {0} alarm in queue, now size is {1}".format(len(alarm_list), self.alarm_queue_.qsize()))
        return
    
    def consume_alarm(self):
        while True:
            time.sleep(1)
            try:
                print("consume_alarm alarm_queue.size is {0}".format(self.alarm_queue_.qsize()))
                while not self.alarm_queue_.empty():
                    #add lock
                    with self.packet_info_lock_:
                        packet_info = self.alarm_queue_.get()
                        chain_hash = int(packet_info.get('chain_hash'))
                        if not packet_info.get('send_timestamp'): # recv info
                            if not self.packet_info_cache_.get(chain_hash):
                                # this is recv info,and befor send info, put it in end of queue again
                                self.alarm_queue_.put(packet_info, block=True, timeout=2)
                                continue
                            else: #recv info and after send info
                                cache_packet_info = self.packet_info_cache_.get(chain_hash)
                                cache_src_node_id = cache_packet_info.get('src_node_id')
                                if cache_src_node_id != packet_info.get('src_node_id'):
                                    print("chain_hash confilct")
                                    continue
    
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
                                self.packet_info_cache_[chain_hash] = cache_packet_info
    
                        else:  # this is send info
                            cache_packet_info =  copy.deepcopy(self.template_packet_info_)
                            cache_packet_info['send_node_id'] = packet_info.get('local_node_id')
                            cache_packet_info['chain_hash'] = int(packet_info.get('chain_hash'))
                            cache_packet_info['chain_msgid'] = int(packet_info.get('chain_msgid'))
                            cache_packet_info['chain_msg_size'] = int(packet_info.get('chain_msg_size'))
                            cache_packet_info['send_timestamp'] = int(packet_info.get('send_timestamp'))
                            cache_packet_info['src_node_id'] = packet_info.get('src_node_id')
                            cache_packet_info['dest_node_id'] = packet_info.get('dest_node_id')
                            cache_packet_info['is_root'] = int(packet_info.get('is_root'))
                            cache_packet_info['broadcast'] = int(packet_info.get('broadcast'))
                            # insert to cache
                            print("insert packet_info: {0}".format(json.dumps(cache_packet_info)))
                            self.packet_info_cache_[chain_hash] = cache_packet_info
                            self.packet_info_chain_hash_.append(chain_hash)
            except Exception as e:
                print('consumer catch exception: {0}'.format(e))
        return

    def dump_db(self):
        while True:
            with self.packet_info_lock_:
                now = int(time.time() * 1000)
                for chain_hash in self.packet_info_chain_hash_:
                    cache_packet_info = self.packet_info_cache_.get(chain_hash)
                    send_timestamp = cache_packet_info.get('send_timestamp')
                    if (now - send_timestamp) < 5 * 60 * 1000:
                        # keep latest 5 min
                        break

                    #TODO(smaug) store cache_packet_info to db

                    # erase chain_hash of this packet_info from cache
                    del self.packet_info_cache_[chain_hash]
                    self.packet_info_chain_hash_.remove(chain_hash)
                
            # wait 5 min until the next dump_db
            time.sleep(5 * 60)
        return 

    # get chain_hash from cache and db
    def get_chain_hash(self, chain_hash):
        with self.packet_info_lock_:
            # TODO(smaug) get from packet_cache first, then from  cache, at last from db
            cache_packet_info = self.packet_info_cache_.get(chain_hash)
            if not cache_packet_info:
                return {}
            return cache_packet_info




