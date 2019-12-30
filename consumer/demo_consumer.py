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


class DemoAlarmConsumer(object):
    def __init__(self, q, queue_key_list, alarm_env = 'test'):
        slog.info("demo alarmconsumer init. pid:{0} paraent:{1} queue_key:{2}".format(os.getpid(), os.getppid(), json.dumps(queue_key_list)))

        self.expire_time_  = 20  # 10min, only focus on latest 10 min
        self.consume_step_ = 20  # get_queue return size for one time
        self.alarm_env_ = alarm_env

        # store packet_info from /api/alarm
        self.alarm_queue_ = q 
        self.queue_key_list_ = queue_key_list # eg: topargus_alarm_list:0 for one consumer bind to one or more queue_key

        # demo sql db client
        self.demo_info_sql_ = DemoInfoSql()
        
        return

    def run(self):
        # usually for one consumer , only handle one type
        slog.info('consume_alarm run')
        if self.alarm_env_ == 'test':
            self.consume_alarm_with_notry()
        else:
            self.consume_alarm()
        return

    def consume_alarm_with_notry(self):
        while True:
            slog.info("begin consume_alarm alarm_queue.size is {0}".format(self.alarm_queue_.qsize(self.queue_key_list_)))
            alarm_payload_list = self.alarm_queue_.get_queue_exp(self.queue_key_list_, self.consume_step_)  # return dict or None
            for alarm_payload in alarm_payload_list:
                alarm_type = alarm_payload.get('alarm_type')
                if alarm_type == 'demo':
                    self.demo_alarm(alarm_payload.get('alarm_content'))
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
                    if alarm_type == 'demo':
                        self.demo_alarm(alarm_payload.get('alarm_content'))
                    else:
                        slog.warn('invalid alarm_type:{0}'.format(alarm_type))
            except Exception as e:
                slog.warn('catch exception:{0}'.format(e))
        return

    # focus on packet_info(drop_rate,hop_num,timing)
    def demo_alarm(self, content):
        slog.info('demo_alarm begin:{0}'.format(json.dumps(content)))
        # TODO(user) do something statictis or calculate

        # dump result to db
        self.dump_db()
        return True


    def dump_db(self):
        slog.info('ready dump to db')
        self.demo_info_sql_.update_insert_to_db()
        return
