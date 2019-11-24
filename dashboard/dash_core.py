#!/usr/bin/env python
#-*- coding:utf8 -*-


import json
import time
import queue
import copy
import os
import threading
from database.packet_sql import PacketInfoSql, PacketRecvInfoSql
from common.slogging import slog


class Dash(object):
    def __init__(self):
        # init db obj
        self.packet_info_sql = PacketInfoSql()
        self.packet_recv_info_sql = PacketRecvInfoSql()

        self.network_ids_lock_ = threading.Lock()
        self.network_ids_cache_filename_ = '/dev/shm/network_ids'
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

    def get_network_id(self, data):
        result = []
        now = int(time.time() * 1000)
        with self.network_ids_lock_:
            # not exist or expired beyond 1 min, then reread from shm
            if not self.network_ids_ or self.network_ids_.get('update_timestamp') < (now - 1 * 60 * 1000):
                if not os.path.exists(self.network_ids_cache_filename_):
                    slog.warn('network_ids_cache_filename_:{0} not exist'.format(self.network_ids_cache_filename_))
                    return result
                with open(self.network_ids_cache_filename_, 'r') as fin:
                    self.network_ids_ = json.loads(fin.read())
                    if not self.network_ids_:
                        slog.warn('read_network_id from filename:{0} failed.'.format(self.network_ids_cache_filename_))
                        return result

                    self.network_ids_['update_timestamp'] = int(time.time() * 1000)
                    slog.info('read_network_id from filename:{0} success. {1}'.format(self.network_ids_cache_filename_, json.dumps(self.network_ids_)))
                    fin.close()

        if data.get('network_id'):
            # get network_id
            for k,v in self.network_ids_.items():
                if k.startswith(network_id) or k == network_id:
                    result.append(v)
            slog.info('get_network_id success. {0}'.format(json.dumps(result)))
            return result
        elif data.get('node_id') or data.get('node_ip'):
            node_ip = ''
            if not data.get('node_id')  and data.get('node_ip'):
                node_ip = data.get('node_ip')
            if data.get('node_id')  and not data.get('node_ip'):
                # get info of node_id
                node_id = data.get('node_id')
                for k,v in self.network_ids_.items():
                    for item in v.get('node_info'):
                        if item.get('node_id').startswith(node_id):
                            node_ip = item.get('node_ip')
                            break
            if not node_ip:
                slog.warn('get_node_ip failed of node_id:{0} node_ip:{1}'.format(data.get('node_id'), data.get('node_ip')))
                return result

            for k,v in self.network_ids_.items():
                for item in v.get('node_info'):
                    if item.get('node_ip') == node_ip:
                        result.append({'node_id': item.get('node_id'), 'size': v.get('size')})
            slog.info('get_network_id of node_id:{0} node_ip:{1} success. result:{2}'.format(data.get('node_id'), data.get('node_ip'), json.dumps(result)))
            return result
        else: # get all network_ids
            result = copy.deepcopy(self.network_ids_) 
            slog.info('get_network_id success. result:{0}'.format(result))
            return result







        

