#!/usr/bin/env python
#-*- coding:utf8 -*-

import sys
import json
import argparse

import os
project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(project_path))
log_path = os.path.join(project_path, "log/topargus-consumer.log")
os.environ['LOG_PATH'] =  log_path
import common.slogging as slogging
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
            'system': [],
            }
    for qkey in all_queue_key:
        if qkey.find('packet') != -1:
            qkey_map['packet'].append(qkey)
        elif qkey.find('networksize') != -1:
            qkey_map['networksize'].append(qkey)
        elif qkey.find('system') != -1:
            qkey_map['system'].append(qkey)

    slog.warn('qkey_map:{0}'.format(json.dumps(qkey_map)))

    consumer_list = []

    if alarm_type == 'packet' or alarm_type == 'all':
        # packet
        for qkey in qkey_map.get('packet'):
            slog.warn('create consumer for packet, assign queue_key:{0}'.format(qkey))
            consumer = packet_consumer.PacketAlarmConsumer(q=mq, queue_key_list = [qkey], alarm_env = alarm_env)
            consumer_list.append(consumer)


    if alarm_type == 'networksize' or alarm_type == 'all':
        qkey = qkey_map.get('networksize')
        qkey.extend(qkey_map.get('system'))
        slog.warn('create consumer for networksize/system, assign queue_key:{0}'.format(json.dumps(list(qkey))))
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
    slogging.start_log_monitor()
    run(alarm_type, alarm_env)
