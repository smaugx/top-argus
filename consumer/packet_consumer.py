#!/usr/bin/env python
#-*- coding:utf8 -*-


import json
import os
import time
import queue
import copy
import threading
from database.packet_sql import PacketInfoSql, PacketRecvInfoSql,NetworkInfoSql
from common.slogging import slog


#{"local_node_id": "010000fc609372cc194a437ae775bdbf00000000d60a7c10e9cc5f94e24cb9c63ee1fba3", "uniq_chain_hash": "416514318958495", "chain_hash": "434300", "chain_msgid": "655361", "chain_msg_size": "9184", "send_timestamp": "1573547749649", "src_node_id": "690000010140ff7fffffffffffffffff0000000032eae48d5405ad0a57173799f7490716", "dest_node_id": "690000010140ff7fffffffffffffffff000000009aee88245d7e31e7abaab1ac9956d5a0", "is_root": "0", "broadcast": "0"}

#{"local_node_id": "010000fc609372cc194a437ae775bdbf00000000d60a7c10e9cc5f94e24cb9c63ee1fba3", "uniq_chain_hash": "1146587997", "chain_hash":"79385948","chain_msgid": "917505", "packet_size": "602", "chain_msg_size": "189", "hop_num": "1", "recv_timestamp": "1573547749394", "src_node_id": "010000ffffffffffffffffffffffffff0000000088ae064b2bb22948a2aee8ecd81c08f9", "dest_node_id": "67000000ff7fff7fffffffffffffffff0000000032eae48d5405ad0a57173799f7490716", "is_root": "0", "broadcast": "0"}

class PacketAlarmConsumer(object):
    def __init__(self, q, queue_key_list):
        slog.info("packet alarmconsumer init. pid:{0} paraent:{1} queue_key:{2}".format(os.getpid(), os.getppid(), json.dumps(queue_key_list)))
        self.expire_time_  = 20  # 10min, only focus on latest 10 min
        self.consume_step_ = 2000 # get_queue return size for one time

        self.packet_recv_info_flag_ = False  # False: will not track or store recv ndoes/ip of packet; True is reverse

        self.packet_info_cache_ = {}
        # keep the order of insert
        self.packet_info_uniq_chain_hash_ = []

        self.packet_recv_info_cache_ = {}  # keep all recv packet befor send packet
        self.packet_recv_uniq_chain_hash_ = []  # keep all recv packet field uniq_chain_hash befor send packet  in order

        # keep all the node_id of some network_id, key is network_id, value is nodes of this network_id
        # something like {'690000010140ff7f': {'node_info': [{'node_id': xxxx, 'node_ip':127.0.0.1:9000}], 'size':1}}
        self.network_ids_ = {}

        # store packet_info from /api/alarm
        self.alarm_queue_ = q 
        self.queue_key_list_ = queue_key_list # eg: topargus_alarm_list:0 for one consumer bind to one or more queue_key
        
        # init db obj
        self.packet_info_sql = PacketInfoSql()
        self.packet_recv_info_sql = PacketRecvInfoSql()
        self.network_info_sql = NetworkInfoSql()

        self.network_info_shm_filename_ = '/dev/shm/topargus_network_info'
        
        #template of packet_info
        self.template_packet_info_ = {
                'uniq_chain_hash': 0,
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
                'dest_networksize': 0,
                'recv_nodes_id': [],   # HexSubstr
                'recv_nodes_ip': [],   # nodeip
                'recv_nodes_num': 0,
                'hop_num': {
                '0_5':0,
                '5_10':0,
                '10_15':0,
                '15_20':0,
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

        return

    def run(self):
        # usually for one consumer , only handle one type
        slog.info('consume_alarm run')
        self.consume_alarm_with_notry()
        #self.consume_alarm()
        return

    def consume_alarm_with_notry(self):
        while True:
            slog.info("begin consume_alarm alarm_queue.size is {0}".format(self.alarm_queue_.qsize(self.queue_key_list_)))
            alarm_payload_list = self.alarm_queue_.get_queue_exp(self.queue_key_list_, self.consume_step_)  # return dict or None
            for alarm_payload in alarm_payload_list:
                alarm_type = alarm_payload.get('alarm_type')
                if alarm_type == 'packet':
                    self.packet_alarm(alarm_payload.get('alarm_content'))
                else:
                    slog.warn('invalid alarm_type:{0}'.format(alarm_type))
        return


    def consume_alarm(self):
        while True:
            slog.info("begin consume_alarm alarm_queue.size is {0}".format(self.alarm_queue_.qsize(self.queue_key_list_)))
            try:
                alarm_payload_list = self.alarm_queue_.get_queue_exp(self.queue_key_list_, self.consume_step_)  # return dict or None
                for alarm_payload in alarm_payload_list:
                    alarm_type = alarm_payload.get('alarm_type')
                    if alarm_type == 'packet':
                        self.packet_alarm(alarm_payload.get('alarm_content'))
                    else:
                        slog.warn('invalid alarm_type:{0}'.format(alarm_type))
            except Exception as e:
                slog.warn('catch exception:{0}'.format(e))
        return

    # focus on packet_info(drop_rate,hop_num,timing)
    def packet_alarm(self, packet_info):
        slog.info('packet_alarm begin:{0}'.format(json.dumps(packet_info)))
        uniq_chain_hash = int(packet_info.get('uniq_chain_hash'))
        now = int(time.time() * 1000)
        ptime = int(packet_info.get('recv_timestamp') or packet_info.get('send_timestamp'))
        if (ptime + self.expire_time_ * 60  *1000) < now:
            slog.info('alarm queue expired: {0} diff:{1} seconds hash:{2}'.format(json.dumps(packet_info), (now - ptime) / 1000, uniq_chain_hash))
            return False

        if not packet_info.get('send_timestamp'): # recv info
            if not self.packet_info_cache_.get(uniq_chain_hash):
                # this is recv info,and befor send info, put it in end of queue again
                tmp_alarm_payload = {
                        'alarm_type': 'packet',
                        'alarm_content': packet_info,
                        }

                if self.packet_recv_info_cache_.get(uniq_chain_hash):
                    self.packet_recv_info_cache_[uniq_chain_hash].append(tmp_alarm_payload)
                else:
                    self.packet_recv_info_cache_[uniq_chain_hash] = [tmp_alarm_payload]
                    self.packet_recv_uniq_chain_hash_.append(uniq_chain_hash)

                if len(self.packet_recv_info_cache_) < 5000:
                    slog.info('hold packet_info: {0}, hold size: {1} hash:{2}'.format(json.dumps(packet_info), len(self.packet_recv_info_cache_), uniq_chain_hash))
                    #time.sleep(0.1)
                    return False 
                else:
                    tmp_remove_recv_uniq_chain_hash_list = []
                    for hash_item in self.packet_recv_uniq_chain_hash_:
                        tmp_packet_info = self.packet_recv_info_cache_.get(hash_item)
                        if not tmp_packet_info:
                            tmp_remove_recv_uniq_chain_hash_list.append(hash_item)
                            continue
                        tmp_ptime = int(tmp_packet_info[0].get('alarm_content').get('recv_timestamp'))
                        if (tmp_ptime + self.expire_time_ * 60  *1000) < now:
                            tmp_remove_recv_uniq_chain_hash_list.append(hash_item)
                            self.packet_recv_info_cache_.pop(hash_item)
                    for remove_hash_item in tmp_remove_recv_uniq_chain_hash_list:
                        self.packet_recv_uniq_chain_hash_.remove(remove_hash_item)
                        slog.warn('remove hold packet, hash:{0}'.format(remove_hash_item))
                    slog.info('hold packet_info size:{0}'.format(len(self.packet_recv_info_cache_)))
                    return False
            else: #recv info and after send info
                cache_packet_info = self.packet_info_cache_.get(uniq_chain_hash)
                cache_src_node_id = cache_packet_info.get('src_node_id')
                if cache_src_node_id != packet_info.get('src_node_id'):
                    slog.info("uniq_chain_hash conflict, hash:{0}".format(uniq_chain_hash))
                    return False
    
                if self.packet_recv_info_flag_:
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
                slog.info("update packet_info: uniq_chain_hash:{0} recv_nodes:{1}".format(cache_packet_info.get('uniq_chain_hash'), cache_packet_info.get('recv_nodes_num')))
                self.packet_info_cache_[uniq_chain_hash] = cache_packet_info
    
        else:  # this is send info
            cache_packet_info =  copy.deepcopy(self.template_packet_info_)
            cache_packet_info['send_node_id'] = packet_info.get('local_node_id')
            cache_packet_info['uniq_chain_hash'] = int(packet_info.get('uniq_chain_hash'))
            cache_packet_info['chain_hash'] = int(packet_info.get('chain_hash'))
            cache_packet_info['chain_msgid'] = int(packet_info.get('chain_msgid'))
            cache_packet_info['chain_msg_size'] = int(packet_info.get('chain_msg_size'))
            cache_packet_info['send_timestamp'] = int(packet_info.get('send_timestamp'))
            cache_packet_info['src_node_id'] = packet_info.get('src_node_id')
            cache_packet_info['dest_node_id'] = packet_info.get('dest_node_id')
            cache_packet_info['is_root'] = int(packet_info.get('is_root'))
            cache_packet_info['broadcast'] = int(packet_info.get('broadcast'))

            networksize = 1
            if cache_packet_info.get('broadcast') == 1:
                networksize = self.get_networksize_from_remote(cache_packet_info['dest_node_id'][:17])  # head 8 * 2 bytes
            cache_packet_info['dest_networksize'] = networksize


            # handle holding recv packet
            if uniq_chain_hash in self.packet_recv_info_cache_:
                slog.debug('handle {0} recv packet'.format(len(self.packet_recv_info_cache_.get(uniq_chain_hash))))

            hold_recv_list = []
            if uniq_chain_hash in self.packet_recv_info_cache_:
                hold_recv_list = self.packet_recv_info_cache_.pop(uniq_chain_hash)
                self.packet_recv_uniq_chain_hash_.remove(uniq_chain_hash)
            for item in hold_recv_list:
                packet_info = item.get('alarm_content')
                cache_src_node_id = cache_packet_info.get('src_node_id')
                if cache_src_node_id != packet_info.get('src_node_id'):
                    slog.info("uniq_chain_hash conflict,hash:{0}".format(uniq_chain_hash))
                    return False
    
                if self.packet_recv_info_flag_:
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
    
            # insert to cache
            slog.info("insert packet_info:{0}".format(json.dumps(cache_packet_info)))
            self.packet_info_cache_[uniq_chain_hash] = cache_packet_info
            self.packet_info_uniq_chain_hash_.append(uniq_chain_hash)

        self.dump_db_packetinfo()
        return True

    def query_network_ids(self,data):
        vs,total = [],0
        vs,total = self.network_info_sql.query_from_db(data, page=1, limit= 1)
        if not vs:
            slog.warn('query network info from db failed')
        return vs, total
    
    def update_network_ids(self, network_id):
        if self.update_network_ids_from_shm():
            return True
        data = {
                'network_id': network_id
                }
        vs, total = self.query_network_ids(data)
        if not vs:
            slog.warn('query network:{0} info from db failed'.format(network_id))
            return False
        self.network_ids_[vs[0].get('network_id')] = json.loads(vs[0].get('network_info'))
        self.network_ids_['update'] = int(time.time() * 1000)
        for k,v in self.network_ids_.items():
            if k == 'update':
                continue
            slog.debug('after update network_id:{0} size:{1}'.format(k, v.get('size')))

        if network_id not in self.network_ids_:
            slog.warn('after update can not get network_info of {0} '.format(network_id))
            print(self.network_ids_.get(network_id))
            return False
        return True

    def update_network_ids_from_shm(self):
        if not os.path.exists(self.network_info_shm_filename_):
            return False
        try:
            with open(self.network_info_shm_filename_, 'r') as fin:
                self.network_ids_ = json.loads(fin.read())
                slog.info('update network_id from shm:{0}'.format(self.network_info_shm_filename_))
                fin.close()
            for k,v in self.network_ids_:
                slog.debug('after update network_id:{0} size:{1}'.format(k, v.get('size')))
            self.network_ids_['update'] = int(time.time() * 1000)
            return True
        except Exception as e:
            slog.warn('catch exception:{0}'.format(e))
            return False

    def get_networksize_from_remote(self, network_id):
        if network_id.startswith('010000'):
            network_id = '010000'
        now = int(time.time() * 1000)
        update = self.network_ids_.get('update') or 0
        slog.debug('diff:{0} secs'.format( (now - update) / 1000))

        if not update or (now - update > 20 * 1000) or (network_id not in self.network_ids_):
            if not self.update_network_ids(network_id):
                return 0

        if network_id not in self.network_ids_:
            slog.warn('can not get network_info of {0}'.format(network_id))
            return 0

        return self.network_ids_[network_id]['size']

    def dump_db_packetinfo(self):
        # packet_info (drop,hop,time...)
        slog.info("dump packet_info to db")
        if len(self.packet_info_uniq_chain_hash_) < 100:
            slog.info('packet cache size:{0} less then 100, will not dump to db'.format(len(self.packet_info_uniq_chain_hash_)))
            return
        now = int(time.time() * 1000)
        tmp_remove_uniq_chain_hash_list = []  # keep ready to remove uniq_chain_hash
        slog.info("uniq_chain_hash size: {0}".format(len(self.packet_info_uniq_chain_hash_)))
        for uniq_chain_hash in self.packet_info_uniq_chain_hash_:
            cache_packet_info = self.packet_info_cache_.get(uniq_chain_hash)
            if not cache_packet_info:
                tmp_remove_uniq_chain_hash_list.append(uniq_chain_hash)
                slog.warn("invalid hash:{0}".format(uniq_chain_hash))
                continue

            slog.info('in dump_db: uniq_chain_hash:{0} recv_nodes:{1}'.format(uniq_chain_hash, cache_packet_info.get('recv_nodes_num')))
            send_timestamp = cache_packet_info.get('send_timestamp')
            if now < send_timestamp:
                slog.info("send_timestamp invalid: {0} hash:{1}".format(send_timestamp, uniq_chain_hash))
                del self.packet_info_cache_[uniq_chain_hash]
                tmp_remove_uniq_chain_hash_list.append(uniq_chain_hash)
                continue

            if (now - send_timestamp) < 5 * 60 * 1000:
                # keep latest 5 min
                slog.info("not expired,keep in list, cache size: {0}".format(len(self.packet_info_uniq_chain_hash_)))
                break 

            #TODO(smaug) store cache_packet_info to db
            recv_nodes_id = cache_packet_info.pop('recv_nodes_id')  # store in table: packet_recv_info_table
            recv_nodes_ip = cache_packet_info.pop('recv_nodes_ip')  # store in table: packet_recv_info_table
            if len(recv_nodes_id) != len(recv_nodes_ip):
                slog.info("recv_nodes_id size:{0} not equal recv_nodes_ip size:{1} hash:{2}".format(len(recv_nodes_id), len(recv_nodes_ip), uniq_chain_hash))
                del self.packet_info_cache_[uniq_chain_hash]
                tmp_remove_uniq_chain_hash_list.append(uniq_chain_hash)
                continue

            if self.packet_recv_info_flag_:
                for nid,nip in zip(recv_nodes_id, recv_nodes_ip):
                    tmp_db_data = {
                            'uniq_chain_hash': uniq_chain_hash,
                            'recv_node_id': nid,
                            'recv_node_ip': nip
                            }
                    slog.info('ready dump to db of uniq_chain_hash recv_node:{0}'.format(json.dumps(tmp_db_data)))
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

            slog.info('ready dump to db of uniq_chain_hash:{0}'.format(json.dumps(cache_packet_info)))
            self.packet_info_sql.update_insert_to_db(cache_packet_info)

            # erase uniq_chain_hash of this packet_info from cache
            del self.packet_info_cache_[uniq_chain_hash]
            tmp_remove_uniq_chain_hash_list.append(uniq_chain_hash)

        for uniq_chain_hash in tmp_remove_uniq_chain_hash_list:
            # remove from list
            self.packet_info_uniq_chain_hash_.remove(uniq_chain_hash)

        return
