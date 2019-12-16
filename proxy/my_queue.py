#!/usr/bin/env python
#-*- coding:utf8 -*-

import redis
import json
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
        self.queue_key_num = 4

        for i in range(0,self.queue_key_num):
            qkey = '{0}:{1}'.format(self.queue_key_base, i)
            self.myredis.sadd(self.all_queue_keys, qkey)
        return
    
    def get_all_queue_keys(self):
        queue_key_list = []
        for i in range(0,self.queue_key_num):
            qkey = '{0}:{1}'.format(self.queue_key_base, i)
            queue_key_list.append(qkey)
        return queue_key_list

    def get_queue_key_with_hash(self, msg_hash = None):
        # eg: topargus_alarm_list:0 ; topargus_alarm_list:1;topargus_alarm_list:2;topargus_alarm_list:3
        qkey = '{0}:{1}'.format(self.queue_key_base, random.randint(0,10000) % self.queue_key_num)
        if msg_hash != None and msg_hash != 0:
            qkey = '{0}:{1}'.format(self.queue_key_base, msg_hash % self.queue_key_num)
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
        qkey = self.get_queue_key_with_hash(item.get('chain_hash'))
        # item is dict, serialize to str
        self.myredis.lpush(qkey, json.dumps(item))
        slog.debug("put type:{0} alarm in queue, now size is {1}".format(item.get('alarm_type'), self.qsize(qkey)))
        return

    def get_queue(self, queue_key):
        # eg: topargus_alarm_list:0 ; topargus_alarm_list:1;topargus_alarm_list:2;topargus_alarm_list:3
        item = self.myredis.brpop(queue_key, timeout=0) # will block here if no data get, return item is tuple
        if not item:
            return None
        return json.loads(item[1])
    

