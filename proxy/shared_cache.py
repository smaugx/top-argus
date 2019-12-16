#!/usr/bin/env python
#-*- coding:utf8 -*-


import copy
from common.slogging import slog
import multiprocessing

# using manager module handle process comunicate
class SharedCache(object):
    def __init__(self):
        manager = multiprocessing.Manager()
        # something like {'690000010140ff7f': {'node_info': [{'node_id': xxxx, 'node_ip':127.0.0.1:9000}], 'size':1}}
        self.network_ids_ = manager.dict()
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
                    return True
            self.network_ids_[network_id]['node_info'].append({'node_id': node_id, 'node_ip': content.get('node_ip')})
            self.network_ids_[network_id]['size']  += 1
            slog.info('add node_id:{0} to network_id:{1}, now size is {2}'.format(node_id, network_id, self.network_ids_[network_id]['size']))
            return True

        return True

    def get_all_network_info(self):
        return self.network_ids_;
