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
        self.mypool  = redis.ConnectionPool(host= '127.0.0.1', port= 6379, password = 'smaugredis')
        self.myredis = redis.StrictRedis(connection_pool = self.mypool)
        self.queue_key = 'topargus_alarm_list'
        return

    def qsize(self):
        return self.myredis.llen(self.queue_key)

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
        self.myredis.lpush(self.queue_key, item)
        return

    def get_queue(self):
        item = myredis.brpop(self.queue_key, timeout=0) # will block here if no data get
        return item
    

