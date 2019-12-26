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
import argparse

from common.slogging import slog
import common.my_queue as my_queue
import common.config as sconfig
from multiprocessing import Process
import networksize_consumer
import packet_consumer


mq = my_queue.RedisQueue(host= sconfig.REDIS_HOST, port=sconfig.REDIS_PORT, password=sconfig.REDIS_PASS)

def run(alarm_type, alarm_env = 'test'):
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

    if alarm_type == 'packet' or alarm_type == 'all':
        # packet
        for qkey in qkey_map.get('packet'):
            slog.warn('create consumer for packet, assign queue_key:{0}'.format(qkey))
            consumer = packet_consumer.PacketAlarmConsumer(q=mq, queue_key_list = [qkey], alarm_env = alarm_env)
            consumer_list.append(consumer)


    if alarm_type == 'networksize' or alarm_type == 'all':
        # networksize and progress
        qkey = qkey_map.get('networksize')
        slog.warn('create consumer for networksize/progress, assign queue_key:{0}'.format(json.dumps(list(qkey))))
        consumer = networksize_consumer.NetworkSizeAlarmConsumer(q=mq, queue_key_list = list(qkey), alarm_env = alarm_env)
        consumer_list.append(consumer)

    # TODO(smaug) add other type here in the future

    if not consumer_list:
        slog.warn("no consumer created")
        return

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
    parser = argparse.ArgumentParser()
    parser.description='TOP-Argus consumer，多进程方式启动一个消费者，绑定到某个类型的报警内容，进行消费'
    parser.add_argument('-t', '--type', help='bind with alarm_type,eg: packet, networksize...', default = '')
    parser.add_argument('-e', '--env', help='env, eg: test,docker', default = 'test')
    args = parser.parse_args()

    if not args.type:
        slog.warn("please give one type or 'all'")
        sys.exit(-1)

    alarm_type = args.type
    alarm_env = args.env
    print('type:{0} env:{1}'.format(alarm_type,alarm_env))
    run(alarm_type, alarm_env)
