#!/usr/bin/env python
#-*- coding:utf8 -*-


import json
import os
import time
import queue
import copy
import threading
from database.packet_sql import NetworkInfoSql, NodeInfoSql,SystemAlarmInfoSql
from common.slogging import slog

PRIORITY_DICT = {
        'high': 2,
        'middle':1,
        'low':0
        }

class NetworkSizeAlarmConsumer(object):
    def __init__(self, q, queue_key_list):
        slog.info("networksize alarmconsumer init. pid:{0} paraent:{1} queue_key:{2}".format(os.getpid(), os.getppid(), json.dumps(queue_key_list)))
        # keep all the node_id of some network_id, key is network_id, value is nodes of this network_id
        # something like {'690000010140ff7f': {'node_info': [{'node_id': xxxx, 'node_ip':127.0.0.1:9000}], 'size':1}}
        self.network_ids_ = {}
        # key is public_ip_port, value is {'public_ip_port':'127.0.0.1:9000','rec':[],'zec':[],....,'val':[]} 
        self.node_info_  = {}

        self.consume_step_ = 30

        # store packet_info from /api/alarm
        self.alarm_queue_ = q 
        self.queue_key_list_ = queue_key_list # eg: topargus_alarm_list:0 for one consumer bind to one or more queue_key
        
        # init db obj
        self.network_info_sql_ = NetworkInfoSql()
        self.system_alarm_info_sql_ = SystemAlarmInfoSql()
        self.node_info_sql_ = NodeInfoSql()
        self.node_info_sql_.delete()
        
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

        if not self.update_node_info(content):
            return
        self.dump_db_node_info(content)
        return

    def networksize_alarm_ent(self, content):
        if not content:
            return False
        node_id = content.get('node_id')
        node_ip = content.get('node_ip')  # ip:port
        network_id = node_id[:17]  # head 8 * 2 bytes

        # attention: specially for kroot_id 010000
        if network_id.startswith('010000'):
            network_id = '010000'
        node_id_status = content.get('node_id_status')
        if node_id_status == 'dead':
            # xtopchain maybe down
            self.remove_dead_node(node_ip)
            return True

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
                    'node_info': [{'node_id': node_id, 'node_ip': node_ip}],
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
            self.network_ids_[network_id]['node_info'].append({'node_id': node_id, 'node_ip': node_ip})
            self.network_ids_[network_id]['size']  += 1
            slog.info('add node_id:{0} to network_id:{1}, now size is {2}'.format(node_id, network_id, self.network_ids_[network_id]['size']))
            return True

        return False

    def dump_db_networksize(self):
        # network_info
        slog.info("dump network_id to db")
        for (k,v) in self.network_ids_.items():
            net_data = {'network_id':k ,'network_info':json.dumps(v)}
            slog.info('dump network_id:{0} size:{1}'.format(k, v.get('size')))
            self.network_info_sql_.update_insert_to_db(net_data)
        return
    
    def load_db_networksize(self):
        # TODO(smaug) not use for now
        return True
        vs,total = [],0
        vs,total = self.network_info_sql_.query_from_db(data)
        if not vs:
            slog.warn('load network_info from db failed')
            return False
        for item in vs:
            self.network_ids_[item.get('network_id')] = json.loads(item.get('network_info'))
            slog.info('load network_info from db ok, network_id:{0} size:{1}'.format(item.get('network_id'), self.network_ids_.get(item.get('network_id')).get('size')))
        return True


    def update_node_info(self, content):
        '''
        network_info = {
                'node_info': [{'node_id': node_id, 'node_ip': content.get('node_ip')}],
                'size': 1,
                }

        # key is public_ip_port, value is {'public_ip_port':'127.0.0.1:9000','rec':[],'zec':[],....,'val':[]} 
        # self.node_info_  = {}
        '''

        if not content:
            return  False
        node_id = content.get('node_id')
        node_ip = content.get('node_ip')  # ip:port
        network_id = node_id[:17]  # head 8 * 2 bytes
        if network_id.startswith('010000'):
            network_id = '010000'
        net_type = 'root'
        if network_id.startswith('6400'):
            net_type = 'rec'
        elif network_id.startswith('6500'):
            net_type = 'zec'
        elif network_id.startswith('6600'):
            net_type = 'edg'
        elif network_id.startswith('6700'):
            net_type = 'arc'
        elif network_id.startswith('6800'):
            net_type = 'adv'
        elif network_id.startswith('6900'):
            net_type = 'val'

        node_id_status = content.get('node_id_status')
        if node_id_status == 'dead':
            if node_ip not in self.node_info_:
                slog.warn('remove node_id:{0} from nonexistent node_info'.format(node_id))
                return  False
            tmp_keys = self.node_info_.get(node_ip).keys()
            for k in tmp_keys:
                if k != 'public_ip_port':
                    # just keep {'public_ip_port':node_ip}
                    self.node_info_[node_ip].remove(k)
            slog.warn('root_node_id:{0} {1} down down down!!!'.format(node_id, node_ip))
            return True

        if node_id_status == 'remove':
            if node_ip not in self.node_info_:
                slog.warn('remove node_id:{0} from nonexistent node_info'.format(node_id))
                return  False
            if not self.node_info_[node_ip].get(net_type):
                slog.warn('remove node_id:{0} from nonexistent node_type:{1}'.format(node_id, net_type))
                return False
            if node_id in self.node_info_[node_ip][net_type]:
                self.node_info_[node_ip][net_type].remove(node_id)
                return True
            return False

        # add
        if node_ip not in self.node_info_:
            # key is public_ip_port, value is {'public_ip_port':'127.0.0.1:9000','rec':[],'zec':[],....,'val':[]} 
            value = {'public_ip_port': node_ip}
            if net_type == 'root':
                value[net_type] = node_id
            else:
                value[net_type] = [node_id] 
            self.node_info_[node_ip] = value
            slog.info('add node_id:{0} {1} to node_info'.format(node_id, node_ip))
            return True 
        
        if self.node_info_.get('public_ip_port') != node_ip:
            if not node_ip.startswith('127.0.0'):
                self.node_info_['public_ip_port'] = node_ip
        if net_type == 'root':
            self.node_info_[node_ip][net_type] = node_id
        else:
            if not self.node_info_[node_ip].get(net_type):
                self.node_info_[node_ip][net_type] = [node_id]
            else:
                self.node_info_[node_ip][net_type].append(node_id)
        slog.info('add node_id:{0} {1} to node_info'.format(node_id, node_ip))
        return True

    def dump_db_node_info(self, content):
        # only remove node or add new node 
        if not content:
            return False
        node_ip = content.get('node_ip')  # ip:port
        node_id = content.get('node_id')
        send_timestamp = content.get('send_timestamp') or int(time.time() * 1000)

        value = copy.deepcopy(self.node_info_.get(node_ip))
        if not value:
            slog.warn('invalid node_id:{0} node_ip:{1}'.format(node_id, node_ip))
            return
        print(value)
        for k,v in value.items():
            if k != 'public_ip_port' and k != 'root':
                value[k] = json.dumps(v)
        self.node_info_sql_.update_insert_to_db(value)
        slog.info("dump node_info to db:{0}".format(json.dumps(value)))
        
        # upadte system_alarm_info
        alarm_info = ''
        root_id = ''
        priority = PRIORITY_DICT.get('low')
        node_id_status = content.get('node_id_status')
        if node_id_status == 'remove':
            alarm_info = 'node_info remove node_id:{0} node_ip:{1}'.format(node_id, node_ip)
        elif node_id_status == 'dead':
            root_id = node_id  # 010000
            alarm_info = 'xtopchain down node_id:{0} node_ip:{1}'.format(node_id, node_ip)
            priority = PRIORITY_DICT.get('high')
        else:
            alarm_info = 'node_info add node_id:{0} node_ip:{1}'.format(node_id, node_ip)

        if not root_id and self.node_info_.get(node_ip):
            root_id = self.node_info_.get(node_ip).get('root') or ''

        self.dump_db_system_alarm_info(node_ip, root_id, priority, alarm_info, send_timestamp)
        return

    def dump_db_system_alarm_info(self, public_ip_port,root = '', priority = 0, alarm_info = '', send_timestamp = 0):
        system_alarm_info = {
                'priority': priority,
                'public_ip_port': public_ip_port,
                'root':root,
                'alarm_info': alarm_info,
                'send_timestamp': send_timestamp
                }
        self.system_alarm_info_sql_.insert_to_db(system_alarm_info)
        slog.debug('insert system_alarm_info to db:{0}'.format(json.dumps(system_alarm_info)))
        return
