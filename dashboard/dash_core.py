#!/usr/bin/env python
#-*- coding:utf8 -*-


import json
import time
import queue
import copy
import os
import threading
from database.packet_sql import PacketInfoSql, PacketRecvInfoSql, NetworkInfoSql
from common.slogging import slog


class Dash(object):
    def __init__(self):
        # init db obj
        self.packet_info_sql = PacketInfoSql()
        self.packet_recv_info_sql = PacketRecvInfoSql()
        self.network_info_sql = NetworkInfoSql()

        self.network_ids_lock_ = threading.Lock()
        self.network_ids_ = {}

    def get_packet_info(self, data):
        vs,total = [],0
        vs,total = self.packet_info_sql.query_from_db(data)
        if not vs:
            slog.debug('packet_info_sql query_from_db failed, data:{0}'.format(json.dumps(data)))
        return vs,total

    def get_packet_recv_info(self, data):
        vs,total = [],0
        vs,total = self.packet_recv_info_sql.query_from_db(data)
        if not vs:
            slog.debug('packet_recv_info_sql query_from_db failed, data:{0}'.format(json.dumps(data)))
        return vs,total

    def query_network_id(self,data):
        vs,total = [],0
        vs,total = self.network_info_sql.query_from_db(data)
        if not vs:
            slog.debug('network_info_sql query_from_db failed, data:{0}'.format(json.dumps(data)))
        return vs,total

    def get_network_id(self, data):
        result =  {
                'node_info': [],
                'node_size': 0,
                }
        now = int(time.time() * 1000)
        node_size = 0
        with self.network_ids_lock_:
            # not exist or expired beyond 1 min, then reread from shm
            if not self.network_ids_ or self.network_ids_.get('update_timestamp').get('update_timestamp') < (now - 1 * 60 * 1000):
                vs,total = self.query_network_id({})
                if not vs:
                    return result
                for item in vs:
                    nid = item.get('network_id')
                    ninfo = item.get('network_info')
                    ninfo = json.loads(ninfo)
                    self.network_ids_[nid] = ninfo

                self.network_ids_['update_timestamp'] = {'update_timestamp': int(time.time() * 1000)}
                slog.info('read_network_id from db success. {0}'.format(json.dumps(self.network_ids_)))

        if data.get('network_id'):
            # get network_id
            for k,v in self.network_ids_.items():
                if k.startswith(data.get('network_id')) or k == data.get('network_id'):
                    if not data.get('onlyszie'):
                        result['node_info'].extend(v.get('node_info'))
                        node_size += len(v.get('node_info'))
                    continue

            result['node_size'] = node_size
            slog.info('get_network_id success. {0}'.format(json.dumps(result)))
            return result
        elif data.get('node_id') or data.get('node_ip'):
            node_ip = data.get('node_ip')
            if not node_ip:
                # get info of node_id
                node_id = data.get('node_id')
                if not node_id:
                    return result

                for k,v in self.network_ids_.items():
                    if node_ip:
                        break
                    if not v or not v.get('node_info'):
                        continue
                    for item in v.get('node_info'):
                        if item.get('node_id').startswith(node_id):
                            node_ip = item.get('node_ip')
                            slog.warn('get_node_ip ok of node_id:{0} node_ip:{1}'.format(data.get('node_id'), node_ip))
                            break
            if not node_ip:
                slog.warn('get_node_ip failed of node_id:{0} node_ip:{1}'.format(data.get('node_id'), data.get('node_ip')))
                return result

            node_size = 0
            for k,v in self.network_ids_.items():
                if not v or not v.get('node_info'):
                    continue
                for item in v.get('node_info'):
                    if item.get('node_ip').split(':')[0] == node_ip.split(':')[0]:
                        if not data.get('onlysize'):
                            result['node_info'].append(item)
                        node_size += 1
            result['node_size'] = node_size
            slog.info('get_network_id of node_id:{0} node_ip:{1} success. result:{2}'.format(data.get('node_id'), data.get('node_ip'), json.dumps(result)))
            return result
        else: # get all network_ids
            result = copy.deepcopy(self.network_ids_) 
            node_size = 0
            for k,v in self.network_ids_:
                if not data.get('onlysize'):
                    result['node_info'].extend(v.get('node_info'))
                node_size += len(v.get('node_info'))
            result['node_size'] = node_size 
            slog.info('get_network_id success. result:{0}'.format(result))
            return result
