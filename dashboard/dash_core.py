#!/usr/bin/env python
#-*- coding:utf8 -*-


import json
import time
import datetime
import random
import queue
import copy
import os
import threading
from database.packet_sql import PacketInfoSql, PacketRecvInfoSql, NetworkInfoSql,DropRateInfoSql
from common.slogging import slog
import common.sipinfo as sipinfo

def get_list_first(l):
    return l[0]


class Dash(object):
    def __init__(self):
        # init db obj
        self.packet_info_sql = PacketInfoSql()
        self.packet_recv_info_sql = PacketRecvInfoSql()
        self.network_info_sql = NetworkInfoSql()
        self.packet_drop_rate_sql = DropRateInfoSql()

        self.network_ids_lock_ = threading.Lock()
        self.network_ids_ = {}

        self.iplocation_ = {}
        self.iplocation_file_ = '/dev/shm/topargus_iplocation'
        self.drop_result_ = []
        
        if os.path.exists(self.iplocation_file_):
            with open(self.iplocation_file_, 'r') as fin:
                self.iplocation_ = json.loads(fin.read())
                fin.close()
            slog.info('load iplocation from {0}, size:{1}'.format(self.iplocation_file_, len(self.iplocation_.keys())))
        return

    def myconverter(self, o):
        if isinstance(o, datetime.datetime):
            return o.__str__()

    def get_packet_info(self, data, limit = 50, page = 1):
        vs,total = [],0
        vs,total = self.packet_info_sql.query_from_db(data, page = page, limit = limit)
        if not vs:
            slog.debug('packet_info_sql query_from_db failed, data:{0}'.format(json.dumps(data)))
        for i in range(0, len(vs)):
            dest_networksize = int(vs[i].get('dest_networksize'))
            recv_nodes_num   = int(vs[i].get('recv_nodes_num'))
            if dest_networksize <= 0 or recv_nodes_num > dest_networksize:
                vs[i]['drop_rate'] = '0.0'
            else:
                drop_rate = 100 - float(recv_nodes_num) / dest_networksize * 100
                drop_rate = float(drop_rate)
                drop_rate = '%.1f' % drop_rate
                vs[i]['drop_rate'] = drop_rate


        return vs,total

    def get_packet_recv_info(self, data, limit = 50, page = 1):
        vs,total = [],0
        vs,total = self.packet_recv_info_sql.query_from_db(data, limit = limit, page = page)
        if not vs:
            slog.debug('packet_recv_info_sql query_from_db failed, data:{0}'.format(json.dumps(data)))
        return vs,total

    def query_network_ids(self,data):
        vs,total = [],0
        vs,total = self.network_info_sql.query_from_db(data)
        if not vs:
            slog.debug('network_info_sql query_from_db failed, data:{0}'.format(json.dumps(data)))
        return vs,total

    def update_network_ids(self):
        vs,total = self.query_network_ids({})
        if not vs:
            return False
        for item in vs:
            nid = item.get('network_id')
            ninfo = item.get('network_info')
            ninfo = json.loads(ninfo)
            self.network_ids_[nid] = ninfo

        self.network_ids_['update_timestamp'] = {'update_timestamp': int(time.time() * 1000)}
        slog.info('read_network_id from db success.')
        return True

    def get_network_ids_exp(self, data):
        result = self.get_network_ids(data)
        if data.get('withip') == False:
            return result

        result_exp = {
                'node_info': [],
                'node_size': 0
                }
        slog.debug('get_network_ids_exp')
        #try:
        for item in result.get('node_info'):
            ip = item.get('node_ip').split(':')[0]
            #'''
            if ip in self.iplocation_:
                item['node_country'] = self.iplocation_[ip]['country_name']
            else:
                ipinfo = sipinfo.GetIPLocation([ip])
                if ipinfo.get(ip):
                    self.iplocation_[ip] = ipinfo.get(ip)
                    item['node_country'] = ipinfo.get(ip).get('country_name')
                    slog.debug('get iplocation of {0} from server'.format(ip))

                    with open(self.iplocation_file_, 'w') as fout:
                        fout.write(json.dumps(self.iplocation_))
                        fout.close()
                else:
                    item['node_country'] = 'unknow' 
            #'''

            '''
            country_name_list = ['United States', 'China', 'England', 'Afric','France']
            tmp_country_name = random.choice(country_name_list)
            item['node_country'] = tmp_country_name
            slog.debug('add country {0}'.format(tmp_country_name))
            '''

            result_exp['node_info'].append(item)
        result_exp['node_size'] = len(result_exp['node_info'])
        #except Exception as e:
        #    slog.warn('parse ip goes wrong: {0}'.format(e))
        return result_exp


    def get_network_ids(self, data):
        result =  {
                'node_info': [],
                'node_size': 0,
                }
        now = int(time.time() * 1000)
        node_size = 0
        with self.network_ids_lock_:
            # not exist or expired beyond 1 min, then reread from shm
            if not self.network_ids_ or self.network_ids_.get('update_timestamp').get('update_timestamp') < (now - 1 * 60 * 1000):
                if not self.update_network_ids():
                    return result
            if data.get('network_id'):
                # get network_id
                for k,v in self.network_ids_.items():
                    if not v or not v.get('node_info'):
                        continue
                    if k.startswith(data.get('network_id')) or k == data.get('network_id'):
                        if data.get('onlysize') != True:
                            result['node_info'].extend(v.get('node_info'))
                        node_size += len(v.get('node_info'))

                result['node_size'] = node_size
                slog.info('get_network_ids success.')
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
                            if data.get('onlysize') != True:
                                result['node_info'].append(item)
                            node_size += 1
                result['node_size'] = node_size
                slog.info('get_network_ids of node_id:{0} node_ip:{1} success. result:{2}'.format(data.get('node_id'), data.get('node_ip'), json.dumps(result)))
                return result
            else: # get all network_ids
                node_size = 0
                for k,v in self.network_ids_.items():
                    if not v or not v.get('node_info'):
                        continue
                    vinfo = v.get('node_info')
                    if not vinfo:
                        continue
                    if data.get('onlysize') != True:
                        result['node_info'].extend(vinfo)
                    node_size += len(vinfo)
                result['node_size'] = node_size 
                slog.info('get_network_ids success. result:{0}'.format(result))
                return result


    def get_network_ids_list(self, virtual = False):
        result =  {
                'network_info': [],
                'network_size': 0,
                }
        now = int(time.time() * 1000)
        node_size = 0
        with self.network_ids_lock_:
            # not exist or expired beyond 1 min, then reread from shm
            if not self.network_ids_ or self.network_ids_.get('update_timestamp').get('update_timestamp') < (now - 1 * 60 * 1000):
                if not self.update_network_ids():
                    return result

            for k,v in self.network_ids_.items():
                if not v or not v.get('node_info'):
                    continue
                if virtual == True:
                    if k == '010000':
                        continue
                else:
                    if k != '010000':
                        continue
                ninfo = {
                        'network_id': k,
                        'network_size': v.get('size')
                        }
                result['network_info'].append(ninfo)
            result['network_size'] = len(result['network_info'])
            return result

     
    # count packet_drop_rate
    def get_packet_drop(self, data):
        begin = data.get('begin')  # ms
        end = data.get('end')      # ms


        # TODO(smaug) just for test, just for better performance
        tnow = int(time.time() * 1000)
        if abs(tnow - end) < 3 * 60 * 1000:   # 3min latest
            if self.drop_result_:
                slog.debug("drop result from cache, size:{0}".format(self.drop_result_))
                return self.drop_result_

        tmp_time = begin

        time_list = []
        time_drop_map = {}
        while  tmp_time <= end:
            tmp_time = tmp_time + 60 * 1000             # 1 min
            time_list.append(tmp_time)
            time_drop_map[tmp_time] = []
        time_list.append(tmp_time)
        time_drop_map[tmp_time] = []

        slog.debug('time_list size {0}'.format(len(time_list)))

        results = []
        dest_node_id = data.get('dest_node_id')
        if not dest_node_id or dest_node_id == None:
            dest_node_id = "allnet"
        # try to get from db first
        drop_vs, drop_total = [], 0
        drop_query_data =  {
                "network_id": dest_node_id,
                "begin": time_list[0],
                "end": time_list[-1]
                }
        drop_vs, drop_total = self.packet_drop_rate_sql.query_from_db(drop_query_data)
        cache_latest_timestamp = 0
        if drop_vs:
            cache_latest_timestamp = int(drop_vs[0].get('timestamp'))
            slog.info('droprate get {0} form cache_db'.format(len(drop_vs)))

        for item in drop_vs:
            k = item.get('timestamp')
            avg_drop_rate = item.get('drop_rate')
            results.append([k, avg_drop_rate])

        if cache_latest_timestamp != 0:
            data['begin'] = cache_latest_timestamp
            slog.info('update begintime {0}'.format(cache_latest_timestamp))

        # get packet info from db
        vs,total = [],0
        limit, page = None, None
        vs,total = self.packet_info_sql.query_from_db(data, limit = limit, page = page)
        if not vs:
            slog.debug('packet_info_sql query_from_db failed, data:{0}'.format(json.dumps(data)))

        #slog.info('from db size:{0} {1}'.format(len(vs), json.dumps(vs, indent = 4, default = self.myconverter)))
        for item in vs:
            del item['timestamp']
            dest_networksize = item.get('dest_networksize')
            recv_nodes_num   = item.get('recv_nodes_num')
            if int(dest_networksize) <= 0:
                slog.warn("dest_networksize smaller than 0")
                continue
            send_timestamp = item.get('send_timestamp')
            time_index = int((int(send_timestamp) - int(begin)) / (60 * 1000))
            drop_rate =  100 - (float(recv_nodes_num) / float(dest_networksize) * 100)
            drop_rate = "%.1f" % drop_rate
            drop_rate = float(drop_rate)
            if recv_nodes_num >= dest_networksize:
                #slog.warn('recv_nodes_num:{0} beyond dest_networksize:{1}'.format(recv_nodes_num, dest_networksize))
                drop_rate = 0.0
            #print('send_timestamp:{0} begin:{1} time_index:{2} recv_nodes_num:{3} dest_networksize:{4} drop_rate:{5}'.format(send_timestamp, begin, time_index, recv_nodes_num, dest_networksize, drop_rate))

            if time_index > (len(time_list) - 1):
                slog.warn('time_index:{0} beyond time_list length:{1}'.format(time_index, len(time_list)))
                continue
            time_drop_map[time_list[time_index]].append(drop_rate)

        
        for k,v in time_drop_map.items():
            if not v:
                continue
            sum_drop_rate = 0.0
            for item in v:
                #slog.debug('drop_rate: {0}'.format(item))
                sum_drop_rate += item
            slog.debug('sum_drop_rate:{0} size:{1}'.format(sum_drop_rate, len(v)))
            avg_drop_rate = sum_drop_rate / len(v)
            avg_drop_rate = "%.1f" % avg_drop_rate 
            avg_drop_rate = float(avg_drop_rate)
            results.append([k, avg_drop_rate])

            tmp_drop_db_item = {
                    "network_id": dest_node_id,
                    "timestamp": k,
                    "drop_rate": avg_drop_rate
                    }
            self.packet_drop_rate_sql.insert_to_db(tmp_drop_db_item)


        results.sort(key=get_list_first)
        self.drop_result_ = results
        '''
        #print(results)
        if results:
            results[0][1] = 1.1
            results[-1][1] = 1.1
        '''
        return results



