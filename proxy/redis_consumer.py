#!/usr/bin/env python
#-*- coding:utf8 -*-

import os 
now_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(now_dir)  #parent dir
activate_this = '%s/vvlinux/bin/activate_this.py' % base_dir
exec(open(activate_this).read())

import sys
sys.path.insert(0, base_dir)

import sys
import json
import requests
import redis
import uuid
import time
import base64
import copy
import core
import threading
from common.slogging import slog
import my_queue

mq = my_queue.RedisQueue(host='127.0.0.1', port=6379, password='')
consumer = core.AlarmConsumer(q=mq)


def run():
    # thread handle alarm and merge packet_info

    consumer_th = threading.Thread(target = consumer.consume_alarm)
    consumer_th.start()

    # thread dump to db
    dumpdb_th = threading.Thread(target = consumer.dump_db)
    dumpdb_th.start()

    #app.run()
    consumer_th.join()
    dumpdb_th.join()


if __name__ == '__main__':
    run()
