#!/usr/bin/env python
#-*- coding:utf8 -*-

import redis
import json
import random
import time
import copy
import queue
import threading
from database.packet_sql import PacketInfoSql, PacketRecvInfoSql,NetworkInfoSql
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
        self.mypool  = redis.ConnectionPool(host = host, port = port, password = password)
        self.myredis = redis.StrictRedis(connection_pool = self.mypool)
        self.all_queue_keys = 'topargus_alarm_allkey_set'
        self.queue_key_base = 'topargus_alarm_list'

        self.queue_key_map = {
                'packet': ['topargus_alarm_list:packet:0', 'topargus_alarm_list:packet:1'],
                'networksize': ['topargus_alarm_list:networksize:0'],
                'progress': ['topargus_alarm_list:networksize:0'],
                #'other':['topargus_alarm_list:other']
                }

        for k,v in self.queue_key_map.items():
            for qkey in v:
                self.myredis.sadd(self.all_queue_keys, qkey)
        return
    
    def get_all_queue_keys(self):
        queue_key_list = set()
        for k,v in self.queue_key_map.items():
            for qkey in v:
                queue_key_list.add(qkey)
        return list(queue_key_list)

    def get_queue_key_of_alarm(self, alarm_type, msg_hash = None):
        # eg: topargus_alarm_list:0 ; topargus_alarm_list:1;topargus_alarm_list:2;topargus_alarm_list:3
        qkey = None
        qkey_list = self.queue_key_map.get(alarm_type)
        if not qkey_list:
            return None

        if len(qkey_list) == 1:
            qkey = qkey_list[0]
            return qkey

        if msg_hash != None:
            msg_hash = int(msg_hash)
            qkey = qkey_list[msg_hash % len(qkey_list)]
        else:
            qkey = qkey_list[random.randint(0,10000) % len(qkey_list)]
        return qkey 

    def qsize(self, queue_key):
        return self.myredis.llen(queue_key)

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
        qkey = self.get_queue_key_of_alarm(item.get('alarm_type'), item.get('alarm_content').get('chain_hash'))
        if qkey == None:
            return
        # item is dict, serialize to str
        self.myredis.lpush(qkey, json.dumps(item))
        slog.debug("put_queue type:{0} in queue {1}, now size is {2}".format(item.get('alarm_type'), qkey, self.qsize(qkey)))
        return

    def get_queue(self, queue_key):
        # eg: topargus_alarm_list:0 ; topargus_alarm_list:1;topargus_alarm_list:2;topargus_alarm_list:3
        item = self.myredis.brpop(queue_key, timeout=0) # will block here if no data get, return item is tuple
        if not item:
            return None
        slog.debug('get_queue from {0} item:{1}'.format(queue_key, item))
        return json.loads(item[1])
    

