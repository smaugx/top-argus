#!/usr/bin/env python
#-*- coding:utf8 -*-


import json
import time
import queue
import copy
import threading
from database.packet_sql import PacketInfoSql, PacketRecvInfoSql
from common.slogging import slog


#{"local_node_id": "010000fc609372cc194a437ae775bdbf00000000d60a7c10e9cc5f94e24cb9c63ee1fba3", "chain_hash": "4165143189", "chain_msgid": "655361", "chain_msg_size": "9184", "send_timestamp": "1573547749649", "src_node_id": "690000010140ff7fffffffffffffffff0000000032eae48d5405ad0a57173799f7490716", "dest_node_id": "690000010140ff7fffffffffffffffff000000009aee88245d7e31e7abaab1ac9956d5a0", "is_root": "0", "broadcast": "0"}

#{"local_node_id": "010000fc609372cc194a437ae775bdbf00000000d60a7c10e9cc5f94e24cb9c63ee1fba3", "chain_hash": "1146587997", "chain_msgid": "917505", "packet_size": "602", "chain_msg_size": "189", "hop_num": "1", "recv_timestamp": "1573547749394", "src_node_id": "010000ffffffffffffffffffffffffff0000000088ae064b2bb22948a2aee8ecd81c08f9", "dest_node_id": "67000000ff7fff7fffffffffffffffff0000000032eae48d5405ad0a57173799f7490716", "is_root": "0", "broadcast": "0"}

class Alarm(object):
    def __init__(self):
        # lock of packet_info_cache_ and packet_info_chain_hash_
        self.packet_info_lock_ = threading.Lock()
        # key is chain_hash, value is packet_info
        self.packet_info_cache_ = {}
        # keep the order of insert
        self.packet_info_chain_hash_ = []
        
        # store packet_info from /api/alarm
        self.alarm_queue_ = queue.Queue(100000) 

        # init db obj
        self.packet_info_sql = PacketInfoSql()
        self.packet_recv_info_sql = PacketRecvInfoSql()
        
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
        
    def put_queue(self, item):
        try:
            self.alarm_queue_.put(item, block=True, timeout = 2)
        except Exception as e:
            slog.info("put queue exception:{0}".format(e))
            return False
        return True

    # handle alarm 
    def handle_alarm(self, alarm_list, alarm_ip):
        if not alarm_list:
            return
    
        for item in alarm_list:
            alarm_type = item.get('alarm_type')

            # TODO(smaug) handle other type
            if alarm_type != 'packet':
                continue

            packet_info = item.get('alarm_content')
            packet_info['public_ip'] = alarm_ip
            self.put_queue(packet_info)
        slog.info("put {0} alarm in queue, now size is {1}".format(len(alarm_list), self.alarm_queue_.qsize()))
        return
    
    def consume_alarm(self):
        while True:
            time.sleep(3)
            try:
                slog.info("consume_alarm alarm_queue.size is {0}".format(self.alarm_queue_.qsize()))
                #while not self.alarm_queue_.empty():
                while self.alarm_queue_.qsize() > 0:
                    #add lock
                    with self.packet_info_lock_:
                        slog.info("begin consume, queue size: {0}".format(self.alarm_queue_.qsize()))
                        packet_info = self.alarm_queue_.get()
                        ptime = packet_info.get('recv_timestamp')
                        if not ptime:
                            ptime = packet_info.get('send_timestamp')
                        ptime = int(ptime)
                        now = int(time.time() * 1000)
                        if (ptime + 5 * 60  *1000) < now:
                            slog.info('alarm queue expired: {0}'.format(json.dumps(packet_info)))
                            continue
                        chain_hash = int(packet_info.get('chain_hash'))
                        if not packet_info.get('send_timestamp'): # recv info
                            if not self.packet_info_cache_.get(chain_hash):
                                # this is recv info,and befor send info, put it in end of queue again
                                #TODO(smaug)
                                self.alarm_queue_.put(packet_info, block=True, timeout=2)
                                if self.alarm_queue_.qsize() < 500:
                                    slog.info('hold packet_info: {0}, queue size: {1}'.format(json.dumps(packet_info), self.alarm_queue_.qsize() ))
                                    time.sleep(0.1)
                                continue
                            else: #recv info and after send info
                                cache_packet_info = self.packet_info_cache_.get(chain_hash)
                                cache_src_node_id = cache_packet_info.get('src_node_id')
                                if cache_src_node_id != packet_info.get('src_node_id'):
                                    slog.info("chain_hash confilct")
                                    continue
    
                                cache_packet_info['recv_nodes_id'].append(packet_info.get('local_node_id'))
                                cache_packet_info['recv_nodes_ip'].append(packet_info.get('public_ip'))
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
                                slog.info("update packet_info: {0}".format(json.dumps(cache_packet_info)))
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
                            slog.info("insert packet_info: {0}".format(json.dumps(cache_packet_info)))
                            self.packet_info_cache_[chain_hash] = cache_packet_info
                            self.packet_info_chain_hash_.append(chain_hash)
            except Exception as e:
                slog.info('consumer catch exception: {0}'.format(e))
        return

    def dump_db(self):
        while True:
            slog.info("dump_db")
            with self.packet_info_lock_:
                now = int(time.time() * 1000)
                tmp_remove_chain_hash_list = []  # keep ready to remove chain_hash
                slog.info("chain_hash size: {0}".format(len(self.packet_info_chain_hash_)))
                for chain_hash in self.packet_info_chain_hash_:
                    cache_packet_info = self.packet_info_cache_.get(chain_hash)
                    if not cache_packet_info:
                        tmp_remove_chain_hash_list.append(chain_hash)
                        continue

                    slog.info('chain_hash{0} cache_packet_info: {1}'.format(chain_hash, json.dumps(cache_packet_info)))
                    send_timestamp = cache_packet_info.get('send_timestamp')
                    if now < send_timestamp:
                        slog.info("send_timestamp invalid: {0}".format(send_timestamp))
                        del self.packet_info_cache_[chain_hash]
                        tmp_remove_chain_hash_list.append(chain_hash)
                        continue

                    if (now - send_timestamp) < 2 * 60 * 1000:
                        # keep latest 5 min
                        slog.info("not expired,keep in list, chain_hash: {0} cache size: {1}".format(chain_hash, len(self.packet_info_chain_hash_)))
                        continue 

                    #TODO(smaug) store cache_packet_info to db
                    recv_nodes_id = cache_packet_info.pop('recv_nodes_id')  # store in table: packet_recv_info_table
                    recv_nodes_ip = cache_packet_info.pop('recv_nodes_ip')  # store in table: packet_recv_info_table
                    if len(recv_nodes_id) != len(recv_nodes_ip):
                        slog.info("recv_nodes_id size:{0} not equal recv_nodes_ip size:{1}".format(len(recv_nodes_id), len(recv_nodes_ip)))
                        del self.packet_info_cache_[chain_hash]
                        tmp_remove_chain_hash_list.append(chain_hash)
                        continue

                    for nid,nip in zip(recv_nodes_id, recv_nodes_ip):
                        tmp_db_data = {
                                'chain_hash': chain_hash,
                                'recv_node_id': nid,
                                'recv_node_ip': nip
                                }
                        slog.info('ready dump to db of chain_hash recv_node:{0}'.format(json.dumps(tmp_db_data)))
                        self.packet_recv_info_sql.insert_to_db(tmp_db_data)

                    '''
                    'hop_num': {'0_5':0,'5_10':0,'10_15':0,'20_':0}
                    'taking': {'0.0_0.5':0,'0.5_1.0':0,'1.0_1.5':0,'1.5_2.0':0,'2.0_':0}
                    '''
                    hop_num = cache_packet_info.pop('hop_num')
                    taking = cache_packet_info.pop('taking')
                    str_hop_num = ''
                    for k,v in hop_num.items():
                        str_hop_num += str(v)
                        str_hop_num += ','
                    # something like '0,12,34,122,'
                    cache_packet_info['hop_num'] = str_hop_num
                    str_taking = ''
                    for k,v in taking.items():
                        str_taking += str(v)
                        str_taking += ','
                    cache_packet_info['taking'] = str_taking

                    slog.info('ready dump to db of chain_hash:{0}'.format(json.dumps(cache_packet_info)))
                    self.packet_info_sql.uniq_insert_to_db(cache_packet_info)

                    # erase chain_hash of this packet_info from cache
                    del self.packet_info_cache_[chain_hash]
                    tmp_remove_chain_hash_list.append(chain_hash)

                for chain_hash in tmp_remove_chain_hash_list:
                    # remove from list
                    self.packet_info_chain_hash_.remove(chain_hash)
                
            # wait 5 min until the next dump_db
            #time.sleep(5 * 60)
            time.sleep(5)
        return 

    # get chain_hash from cache and db
    def get_chain_hash(self, chain_hash):
        with self.packet_info_lock_:
            # TODO(smaug) get from packet_cache first, then from  cache, at last from db
            cache_packet_info = self.packet_info_cache_.get(chain_hash)
            if not cache_packet_info:
                return {}
            return cache_packet_info




