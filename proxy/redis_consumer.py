#!/usr/bin/env python
#-*- coding:utf8 -*-

import os 
now_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(now_dir)  #parent dir
activate_this = '%s/vvlinux/bin/activate_this.py' % base_dir
exec(open(activate_this).read())

import sys
sys.path.insert(0, base_dir)

import core
from common.slogging import slog
import my_queue
import shared_cache
from multiprocessing import Process

mq = my_queue.RedisQueue(host='127.0.0.1', port=6379, password='')
scache = shared_cache.SharedCache()


def run():
    global mq, scache
    all_queue_key = mq.get_all_queue_keys()  # set of queue_key
    consumer_list = []
    for item in all_queue_key:
        consumer = core.AlarmConsumer(q=mq, queue_key = item, sharedcache = scache)
        consumer_list.append(consumer)

    process_list = []
    for c in consumer_list:
        p = Process(target=c.run)
        p.start()
        process_list.append(p)

    slog.info('{0} consumer started'.format(len(consumer_list)))

    for p in process_list:
        p.join()

    return


if __name__ == '__main__':
    run()