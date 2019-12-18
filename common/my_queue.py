#!/usr/bin/env python
#-*- coding:utf8 -*-

import redis
import json
import hashlib
import random
import queue
from common.slogging import slog

class CacheQueue(object):
    def __init__(self):
        self.alarm_queue_ = queue.Queue(100000) 
        return

    def qsize(self):
        return self.alarm_queue_.qsize()

    # handle alarm 
    def handle_alarm(self, data):
        if not data:
            return
    
        for item in data:
            # item is string ,not dict
            self.put_queue(item)
        slog.debug("put {0} alarm in queue, now size is {1}".format(len(data), self.qsize()))
        return

    def put_queue(self, item):
        if not isinstance(item, str):
            return
        self.alarm_queue_.put(item, block=False, timeout=1)
        return

    def get_queue(self):
        item = self.alarm_queue_.get(block=True)  # will block here if no data get
        return item
    

class RedisQueue(object):
    def __init__(self, host, port, password):
        self.mypool  = redis.ConnectionPool(host = host, port = port, password = password, decode_responses=True)
        self.myredis = redis.StrictRedis(connection_pool = self.mypool)
        self.all_queue_keys = 'topargus_alarm_allkey_set'
        self.queue_key_base = 'topargus_alarm_list'
        self.alarm_type_queue_num = 4   # every type has 4 queue
        self.all_queue_keys_set = set()  # keep all queue_key in cache

        # add already known type
        for i in range(0, self.alarm_type_queue_num):
            qkey_packet = '{0}:packet:{1}'.format(self.queue_key_base, i)
            self.myredis.sadd(self.all_queue_keys, qkey_packet)
            self.all_queue_keys_set.add(qkey_packet)

            qkey_net = '{0}:networksize:{1}'.format(self.queue_key_base, i)
            self.myredis.sadd(self.all_queue_keys, qkey_net)
            self.all_queue_keys_set.add(qkey_net)

            qkey_pro = '{0}:progress:{1}'.format(self.queue_key_base, i)
            self.myredis.sadd(self.all_queue_keys, qkey_pro)
            self.all_queue_keys_set.add(qkey_pro)

        return
    
    def get_all_queue_keys(self):
        ret = self.myredis.smembers(self.all_queue_keys)
        return list(ret)

    def get_queue_key_of_alarm(self, alarm_item):
        # attention: using right field as hash value, will reduce progress communication
        alarm_type = alarm_item.get('alarm_type')
        msg_hash = None
        if alarm_type == 'packet':
            msg_hash = int(alarm_item.get('alarm_content').get('chain_hash'))
        elif alarm_type == 'networksize' or alarm_type == 'progress':
            node_id = alarm_item.get('alarm_content').get('node_id') 
            network_id = node_id[:17]  # head 8 * 2 bytes
            if network_id.startswith('010000'):
                network_id = '010000'

            msg_hash = int(int(hashlib.sha256(network_id.encode('utf-8')).hexdigest(), 16) % 10**8)
        else:
            msg_hash = random.randint(0,10000)

        # eg: topargus_alarm_list:type:0 ; topargus_alarm_list:type:1
        index = msg_hash % self.alarm_type_queue_num   # 0,1,2,3
        qkey = '{0}:{1}:{2}'.format(self.queue_key_base, alarm_type, index)
        if qkey not in self.all_queue_keys_set:
            self.myredis.sadd(self.all_queue_keys, qkey)
            self.all_queue_keys_set.add(qkey)

        slog.debug('get qkey:{0}'.format(qkey))
        return qkey 

    def qsize(self, queue_key_list):
        if not queue_key_list:
            return 0
        # always return the first list (high level priority)
        return self.myredis.llen(queue_key_list[0])

    # handle alarm 
    def handle_alarm(self, data):
        if not data:
            return
    
        for item in data:
            self.put_queue(item)
        return

    def put_queue(self, item):
        if not isinstance(item, dict):
            return
        # TODO(smaug) for packet using chain_hash; other type using other hash

        qkey = self.get_queue_key_of_alarm(item)
        # item is dict, serialize to str
        # TODO(smaug)
        size = self.qsize([qkey])
        if size >= 500000:
            slog.warn("queue_key:{0} size {1} beyond 500000".format(qkey, size))
            return
        self.myredis.lpush(qkey, json.dumps(item))
        slog.debug("put_queue alarm:{0} in queue {1}, now size is {2}".format(json.dumps(item), qkey, self.qsize([qkey])))
        return

    # queue_key_list :[ 'topargus_alarm_list:packet:0', 'topargus_alarm_list:packet:1']
    def get_queue(self, queue_key_list):
        item = self.myredis.brpop(queue_key_list, timeout=0) # will block here if no data get, return item is tuple
        if not item:
            return None
        slog.debug('get_queue {0}'.format(item))
        return json.loads(item[1])
    
    # get multi-item one time
    def get_queue_exp(self, queue_key_list, step = 50):
        item_list = []
        for i in range(0, step):
            item = self.get_queue(queue_key_list)
            if item != None:
                item_list.append(item)
        slog.debug('get_queue multi-item size:{0}'.format(len(item_list)))
        return item_list
