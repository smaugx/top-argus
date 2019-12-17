#!/usr/bin/env python
#-*- coding:utf8 -*-

import os 
now_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(now_dir)  #parent dir
activate_this = '%s/vvlinux/bin/activate_this.py' % base_dir
exec(open(activate_this).read())

import sys
sys.path.insert(0, base_dir)
import json

from common.slogging import slog
import common.my_queue as my_queue
from multiprocessing import Process
import networksize_consumer
import packet_consumer


mq = my_queue.RedisQueue(host='127.0.0.1', port=6379, password='')

def run():
    global mq
    all_queue_key = mq.get_all_queue_keys()  # set of queue_key
    qkey_map = {
            'packet': [],
            'networksize': [],
            'progress': [],
            }
    for qkey in all_queue_key:
        if qkey.find('packet') != -1:
            qkey_map['packet'].append(qkey)
        elif qkey.find('networksize') != -1:
            qkey_map['networksize'].append(qkey)
        elif qkey.find('progress') != -1:
            qkey_map['progress'].append(qkey)

    slog.warn('qkey_map:{0}'.format(json.dumps(qkey_map)))

    consumer_list = []

    # packet
    for qkey in qkey_map.get('packet'):
        slog.warn('create consumer for packet, assign queue_key:{0}'.format(qkey))
        consumer = packet_consumer.PacketAlarmConsumer(q=mq, queue_key_list = [qkey])
        consumer_list.append(consumer)


    # networksize and progress
    for qkey in zip(qkey_map.get('progress'), qkey_map.get('networksize')):
        slog.warn('create consumer for networksize/progress, assign queue_key:{0}'.format(json.dumps(list(qkey))))
        consumer = networksize_consumer.NetworkSizeAlarmConsumer(q=mq, queue_key_list = list(qkey))
        consumer_list.append(consumer)

    print(consumer_list)

    process_list = []
    for c in consumer_list:
        p = Process(target=c.run)
        process_list.append(p)

    slog.warn('{0} consumer started, ==== start'.format(len(consumer_list)))

    for p in process_list:
        p.start()

    for p in process_list:
        p.join()

    return


if __name__ == '__main__':
    run()
