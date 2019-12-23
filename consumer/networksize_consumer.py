#!/usr/bin/env python
#-*- coding:utf8 -*-


import json
import os
import time
import queue
import copy
import threading
from database.packet_sql import NetworkInfoSql
from common.slogging import slog


class NetworkSizeAlarmConsumer(object):
    def __init__(self, q, queue_key_list):
        slog.info("networksize alarmconsumer init. pid:{0} paraent:{1} queue_key:{2}".format(os.getpid(), os.getppid(), json.dumps(queue_key_list)))
        # keep all the node_id of some network_id, key is network_id, value is nodes of this network_id
        # something like {'690000010140ff7f': {'node_info': [{'node_id': xxxx, 'node_ip':127.0.0.1:9000}], 'size':1}}
        self.network_ids_ = {}

        self.consume_step_ = 30

        # store packet_info from /api/alarm
        self.alarm_queue_ = q 
        self.queue_key_list_ = queue_key_list # eg: topargus_alarm_list:0 for one consumer bind to one or more queue_key
        
        # init db obj
        self.network_info_sql = NetworkInfoSql()
        
    def run(self):
        # usually for one consumer , only handle one type
        slog.info('consume_alarm run')
        self.consume_alarm_with_notry()
        #self.consume_alarm()
        return

    def consume_alarm_with_notry(self):
        while True:
            slog.info("begin consume_alarm alarm_queue.size is {0}".format(self.alarm_queue_.qsize(self.queue_key_list_)))
            alarm_payload_list = self.alarm_queue_.get_queue_exp(self.queue_key_list_, self.consume_step_)  # return dict or None
            for alarm_payload in alarm_payload_list:
                alarm_type = alarm_payload.get('alarm_type')
                if alarm_type == 'networksize':
                    self.networksize_alarm(alarm_payload.get('alarm_content'))
                elif alarm_type == 'progress':
                    self.progress_alarm(alarm_payload.get('alarm_content'))
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
                    if alarm_type == 'networksize':
                        self.networksize_alarm(alarm_payload.get('alarm_content'))
                    elif alarm_type == 'progress':
                        self.progress_alarm(alarm_payload.get('alarm_content'))
                    else:
                        slog.warn('invalid alarm_type:{0}'.format(alarm_type))
            except Exception as e:
                slog.warn('catch exception:{0}'.format(e))
        return


    def get_networksize(self, network_id):
        if network_id.startswith('010000'):
            network_id = '010000'
        if network_id not in self.network_ids_:
            return 0
        return self.network_ids_[network_id]['size']

    def get_node_ip(self, node_id):
        network_id = node_id[:17]  # head 8 * 2 bytes
        if network_id.startswith('010000'):
            network_id = '010000'
        if network_id not in self.network_ids_:
            return ''
        for ni in self.network_ids_[network_id]['node_info']:
            if ni.get('node_id') == node_id:
                return ni.get('node_ip')
        slog.warn('get no node_ip of node_id:{0}'.format(node_id))
        return ''

    def remove_dead_node(self, node_ip):
        network_ids_bak = copy.deepcopy(self.network_ids_)
        for k,v in network_ids_bak.items():
            for i in range(len(v.get('node_info'))):
                ni = v.get('node_info')[i]
                if ni.get('node_ip') == node_ip:
                    del self.network_ids_[k]['node_info'][i]
                    self.network_ids_[k]['size'] -= 1
                    slog.warn('remove dead node_id:{0} node_ip:{1}'.format(ni.get('node_id'), ni.get('node_ip')))
            if len(self.network_ids_[k]['node_info']) == 0:
                del self.network_ids_[k]
        for k,v in self.network_ids_.items():
            slog.info('network_ids key:{0} size:{1}'.format(k,v.get('size')))
        return


    def networksize_alarm(self, content):
        if not self.networksize_alarm_ent(content):
            return

        # something updated
        self.dump_db_networksize()
        return

    def networksize_alarm_ent(self, content):
        if not content:
            return False
        node_id = content.get('node_id')
        network_id = node_id[:17]  # head 8 * 2 bytes

        # attention: specially for kroot_id 010000
        if network_id.startswith('010000'):
            network_id = '010000'
        node_id_status = content.get('node_id_status')
        if node_id_status == 'remove':
            if network_id not in self.network_ids_:
                slog.warn('remove node_id:{0} from nonexistent network_id:{1}'.format(node_id, network_id))
                return False
            for ni in self.network_ids_[network_id]['node_info']:
                if ni.get('node_id') == node_id:
                    self.network_ids_[network_id]['node_info'].remove(ni)
                    self.network_ids_[network_id]['size'] -= 1
                    slog.info('remove node_id:{0} from network_id:{1}, now size:{2}'.format(node_id, network_id, self.network_ids_[network_id]['size']))
                    break
            return True

        # normal or add
        if network_id not in self.network_ids_:
            network_info = {
                    'node_info': [{'node_id': node_id, 'node_ip': content.get('node_ip')}],
                    'size': 1,
                    }
            self.network_ids_[network_id] = network_info
            slog.info('add node_id:{0} to network_id:{1}, new network_id and now size is 1'.format(node_id, network_id))
            return True
        else:
            for ni in self.network_ids_[network_id]['node_info']:
                if ni.get('node_id') == node_id:
                    #slog.debug('already exist node_id:{0} in network_id:{1}'.format(node_id, network_id))
                    return False
            self.network_ids_[network_id]['node_info'].append({'node_id': node_id, 'node_ip': content.get('node_ip')})
            self.network_ids_[network_id]['size']  += 1
            slog.info('add node_id:{0} to network_id:{1}, now size is {2}'.format(node_id, network_id, self.network_ids_[network_id]['size']))
            return True

        return False

    def progress_alarm(self, content):
        if not self.progress_alarm_ent(content):
            return

        self.dump_db_networksize()
        return

    # recv progress alarm,like down,high cpu,high mem...
    # TODO(smaug)
    def progress_alarm_ent(self, content):
        now = int(time.time() * 1000)
        if now - content.get('timestamp') > 10 * 60 * 1000:
            slog.warn('ignore alarm:{0}'.format(json.dumps(content)))
            return False
        node_id = content.get('node_id')
        info = content.get('info')
        slog.info(info)
        node_ip = self.get_node_ip(node_id)
        slog.info('get_node_ip {0} of node_id:{1}'.format(node_ip, node_id))
        if not node_ip:
            return False
        self.remove_dead_node(node_ip)
        return True


    def dump_db_networksize(self):
        # network_info
        slog.info("dump network_id to db")
        for (k,v) in self.network_ids_.items():
            net_data = {'network_id':k ,'network_info':json.dumps(v)}
            slog.info('dump network_id:{0} size:{1}'.format(k, v.get('size')))
            self.network_info_sql.update_insert_to_db(net_data)
        return
