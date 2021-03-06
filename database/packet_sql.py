# -*- coding:utf-8 -*-
from database.bean import Bean
import time
import json
from common.slogging import slog

class PacketInfoSql(Bean):
    _tbl = 'packet_info_table'  #所有发包收包信息发在一个表中
    _cols = 'uniq_chain_hash,chain_hash,chain_msgid,chain_msg_size,packet_size,send_timestamp,is_root,broadcast,send_node_id,src_node_id,dest_node_id,dest_networksize,recv_nodes_num,hop_num,taking,timestamp'

    def __init__(self):
        slog.info('PacketInfoSql init')
        return

    #TODO 增加 timestamp 范围
    #name is something like 'bepo retry';priority is list,different from __init__()
    #def query(cls,id ,gid , service_name , type  ,name ,priority ,page = 1, limit = 50):
    @classmethod
    def query_from_db(cls,data,cols = None, page = 1, limit = 50):
        sbegin = int(time.time() * 1000)
        where ,vs,total = [],[],0

        if data.get('uniq_chain_hash'):
            where.append(' uniq_chain_hash = {0} '.format(data.get('uniq_chain_hash')))

        if data.get('chain_hash'):
            where.append(' chain_hash = {0} '.format(data.get('chain_hash')))

        if data.get('chain_msgid'):
            where.append(' chain_msgid = {0} '.format(data.get('chain_msgid')))

        if data.get('is_root'):
            where.append(' is_root = {0} '.format(data.get('is_root')))

        if data.get('broadcast'):
            where.append(' broadcast = {0} '.format(data.get('broadcast')))

        if data.get('send_node_id'):
            where.append(' send_node_id = {0} '.format(data.get('send_node_id')))

        if data.get('src_node_id'):
            if len(data.get('src_node_id')) <= 12:
                where.append(' src_node_id regexp "^{0}" '.format(data.get('src_node_id')))
            else:
                where.append(' src_node_id = "{0}" '.format(data.get('src_node_id')))

        if data.get('dest_node_id'):
            if len(data.get('dest_node_id')) <= 20:
                where.append(' dest_node_id regexp "^{0}" '.format(data.get('dest_node_id')))
            else:
                where.append(' dest_node_id = "{0}" '.format(data.get('dest_node_id')))

        if data.get('begin'):
            where.append(' `send_timestamp` >= {0} '.format(data.get('begin')))
        if data.get('end'):
            where.append(' `send_timestamp` <= {0} '.format(data.get('end')))

        where = ' and '.join(where)
        vs,total = [],0
        #vs = cls.select_vs(cols = cols, where=where, page=page, limit=limit, order=' timestamp desc ')
        vs = cls.select_vs(cols = cols, where=where, page=page, limit=limit, order=' send_timestamp desc ')
        total = cls.total(where = where )
        send = int(time.time() * 1000)
        slog.debug('select * from %s where %s,total: %s taking:%d ms' % (cls._tbl,where,total,(send - sbegin)))
        return vs, total

    @classmethod
    def ignore_insert_to_db(cls,data):
        return cls.ignore_insert(data = data)

    @classmethod
    def update_insert_to_db(cls,data):
        return cls.update_insert(data = data)

    @classmethod
    def insert_to_db(cls,data):
        return cls.insert(data = data)
    
    @classmethod
    def update_incry(cls,clause):
        print('update table %s: %s ' % (cls._tbl,clause))
        return cls.update(clause = clause)


    @classmethod
    def update_case(cls,data=None, where=''):
        print('update table packet_info_table: %s where:%s' % (json.dumps(data),where))
        return cls.update_dict(data = data, where = where )


# store packet recv node_id and ip
class PacketRecvInfoSql(Bean):
    _tbl = 'packet_recv_info_table'  #所有发包收包信息发在一个表中
    _cols = 'uniq_chain_hash,recv_node_id,recv_node_ip'

    def __init__(self):
        return

    #TODO 增加 timestamp 范围
    #name is something like 'bepo retry';priority is list,different from __init__()
    #def query(cls,id ,gid , service_name , type  ,name ,priority ,page = 1, limit = 50):
    @classmethod
    def query_from_db(cls,data,cols = None, page = 1, limit = 50):
        sbegin = int(time.time() * 1000)
        where ,vs,total = [],[],0

        if data.get('uniq_chain_hash'):
            where.append(' uniq_chain_hash = {0} '.format(data.get('uniq_chain_hash')))

        if data.get('recv_node_id'):
            if len(data.get('recv_node_id')) <= 12:
                where.append(' recv_node_id regexp "^{0}" '.format(data.get('recv_node_id')))
            else:
                where.append(' recv_node_id = "{0}" '.format(data.get('recv_node_id')))

        if data.get('recv_node_ip'):
            if len(data.get('recv_node_ip')) <= 12:
                where.append(' recv_node_ip regexp "{0}" '.format(data.get('recv_node_ip')))
            else:
                where.append(' recv_node_ip = "{0}" '.format(data.get('recv_node_ip')))

        where = ' and '.join(where)
        vs,total = [],0
        vs = cls.select_vs(cols = cols, where=where, page=page, limit=limit, order='')
        total = cls.total(where = where )
        send = int(time.time() * 1000)
        slog.debug('select * from %s where %s,total: %s taking:%d ms' % (cls._tbl,where,total, (send - sbegin)))
        return vs, total

    @classmethod
    def ignore_insert_to_db(cls,data):
        return cls.ignore_insert(data = data)

    @classmethod
    def update_insert_to_db(cls,data):
        return cls.update_insert(data = data)


    @classmethod
    def insert_to_db(cls,data):
        return cls.insert(data = data)
    
    @classmethod
    def update_incry(cls,clause):
        print('update table %s: %s ' % (cls._tbl,clause))
        return cls.update(clause = clause)


    @classmethod
    def update_case(cls,data=None, where=''):
        print('update table packet_recv_info_table: %s where:%s' % (json.dumps(data),where))
        return cls.update_dict(data = data, where = where )


# store network_id node_id and ip 
class NetworkInfoSql(Bean):
    _tbl = 'network_info_table'
    _cols = 'network_id,network_info'

    def __init__(self):
        return

    @classmethod
    def query_from_db(cls,data,cols = None,page = 1, limit = 50):
        sbegin = int(time.time() * 1000)
        where ,vs,total = [],[],0

        if data.get('network_id'):
            if len(data.get('network_id')) <= 20:
                where.append(' network_id regexp "^{0}" '.format(data.get('network_id')))
            else:
                where.append(' network_id = "{0}" '.format(data.get('network_id')))

        where = ' and '.join(where)
        vs,total = [],0

        vs = cls.select_vs(cols = cols, where=where, page=page, limit=limit, order='')
        total = cls.total(where = where )
        send = int(time.time() * 1000)
        slog.debug('select * from %s where %s,total: %s taking:%d ms' % (cls._tbl,where,total,(send - sbegin)))
        return vs, total

    @classmethod
    def ignore_insert_to_db(cls,data):
        return cls.ignore_insert(data = data)

    @classmethod
    def update_insert_to_db(cls,data):
        return cls.update_insert(data = data)

    @classmethod
    def insert_to_db(cls,data):
        return cls.insert(data = data)
    
    @classmethod
    def update_incry(cls,clause):
        print('update table %s: %s ' % (cls._tbl,clause))
        return cls.update(clause = clause)

    @classmethod
    def update_case(cls,data=None, where=''):
        print('update table network_info_table: %s where:%s' % (json.dumps(data),where))
        return cls.update_dict(data = data, where = where )


# drop_rate of network_id
class DropRateInfoSql(Bean):
    _tbl = 'packet_drop_info_table'
    _cols = 'network_id,timestamp,drop_rate'

    def __init__(self):
        return

    @classmethod
    def query_from_db(cls,data,cols = None, page = 1, limit = 50):
        sbegin = int(time.time() * 1000)
        where ,vs,total = [],[],0

        if data.get('network_id'):
            if len(data.get('network_id')) <= 20:
                where.append(' network_id regexp "^{0}" '.format(data.get('network_id')))
            else:
                where.append(' network_id = "{0}" '.format(data.get('network_id')))


        if data.get('begin'):
            where.append(' `timestamp` >= {0} '.format(data.get('begin')))
        if data.get('end'):
            where.append(' `timestamp` <= {0} '.format(data.get('end')))

        where = ' and '.join(where)
        vs,total = [],0
        vs = cls.select_vs(cols = cols, where=where, page=page, limit=limit, order=' timestamp desc')
        total = cls.total(where = where )
        send = int(time.time() * 1000)
        slog.debug('select * from %s where %s,total: %s taking:%d ms' % (cls._tbl,where,total, (send - sbegin)))
        return vs, total

    @classmethod
    def ignore_insert_to_db(cls,data):
        return cls.ignore_insert(data = data)

    @classmethod
    def update_insert_to_db(cls,data):
        return cls.update_insert(data = data)

    @classmethod
    def insert_to_db(cls,data):
        return cls.insert(data = data)
    
    @classmethod
    def update_incry(cls,clause):
        print('update table %s: %s ' % (cls._tbl,clause))
        return cls.update(clause = clause)

    @classmethod
    def update_case(cls,data=None, where=''):
        print('update table network_info_table: %s where:%s' % (json.dumps(data),where))
        return cls.update_dict(data = data, where = where )


# store node_info 
class NodeInfoSql(Bean):
    _tbl = 'node_info_table'
    _cols = 'public_ip_port,root,status,rec,zec,edg,arc,adv,val'

    def __init__(self):
        return

    @classmethod
    def query_from_db(cls,data,cols = None,page = 1, limit = 2000):
        sbegin = int(time.time() * 1000)
        where ,vs,total = [],[],0

        if data.get('public_ip_port'):
            where.append(' `public_ip_port` = "{0}" '.format(data.get('public_ip_port')))
        if data.get('root'):
            if len(data.get('root')) <= 20:
                where.append(' `root` regexp "{0}" '.format(data.get('root')))
            else:
                where.append(' `root` = "{0}" '.format(data.get('root')))
        if data.get('status'):  # online or offline
            where.append(' `status` = "{0}" '.format(data.get('status')))
        if data.get('rec'):
            where.append(' `rec` like "%%{0}%%" '.format(data.get('rec')))
        if data.get('zec'):
            where.append(' `zec` like "%%{0}%%" '.format(data.get('zec')))
        if data.get('edg'):
            where.append(' `edg` like "%%{0}%%" '.format(data.get('edg')))
        if data.get('arc'):
            where.append(' `arc` like "%%{0}%%" '.format(data.get('arc')))
        if data.get('adv'):
            where.append(' `adv` like "%%{0}%%" '.format(data.get('adv')))
        if data.get('val'):
            where.append(' `val` like "%%{0}%%" '.format(data.get('val')))

        where = ' and '.join(where)
        vs,total = [],0

        vs = cls.select_vs(cols = cols, where=where, page=page, limit=limit, order='')
        total = cls.total(where = where )
        send = int(time.time() * 1000)
        slog.debug('select * from %s where %s,total: %s taking:%d ms' % (cls._tbl,where,total,(send - sbegin)))
        return vs, total

    @classmethod
    def ignore_insert_to_db(cls,data):
        return cls.ignore_insert(data = data)

    @classmethod
    def update_insert_to_db(cls,data):
        return cls.update_insert(data = data)

    @classmethod
    def insert_to_db(cls,data):
        return cls.insert(data = data)
    
    @classmethod
    def update_incry(cls,clause):
        print('update table %s: %s ' % (cls._tbl,clause))
        return cls.update(clause = clause)

    @classmethod
    def update_case(cls,data=None, where=''):
        print('update table node_info_table: %s where:%s' % (json.dumps(data),where))
        return cls.update_dict(data = data, where = where )

    @classmethod
    def delete_db(cls,data):
        sbegin = int(time.time() * 1000)
        where = []
        if data.get('public_ip_port'):
            where.append(' `public_ip_port` = "{0}" '.format(data.get('public_ip_port')))
        if data.get('root'):
            if len(data.get('root')) <= 20:
                where.append(' `root` regexp "{0}" '.format(data.get('root')))
            else:
                where.append(' `root` = "{0}" '.format(data.get('root')))

        where = ' and '.join(where)
        cls.delete(where = where)
        send = int(time.time() * 1000)
        slog.debug('delete from %s where %s taking:%d ms' % (cls._tbl,where,(send - sbegin)))
        return


# store system_alarm_info 
class SystemAlarmInfoSql(Bean):
    _tbl = 'system_alarm_info_table'
    _cols = 'id,priority,public_ip_port,root,alarm_info,send_timestamp'

    def __init__(self):
        return

    @classmethod
    def query_from_db(cls,data,cols = None,page = 1, limit = 200):
        sbegin = int(time.time() * 1000)
        where ,vs,total = [],[],0

        if data.get('public_ip_port'):
            where.append(' `public_ip_port` = "{0}" '.format(data.get('public_ip_port')))
        if data.get('root'):
            if len(data.get('root')) <= 20:
                where.append(' `root` regexp "{0}" '.format(data.get('root')))
            else:
                where.append(' `root` = "{0}" '.format(data.get('root')))
        if data.get('priority'): # list of priority, eg: [0,1,2] ,0 is low, 1 is middle, 2 is high
            wp = []
            for p in data.get('priority'):
                if p not in [0,1,2]:
                    continue
                wp.append(' `priority` = "{0}" '.format(p))
            wp = ' or '.join(wp)
            if wp:
                wp = ' ( {0} ) '.format(wp)
                where.append(wp)

        if data.get('begin'):
            where.append(' `send_timestamp` >= {0} '.format(data.get('begin')))
        if data.get('end'):
            where.append(' `send_timestamp` <= {0} '.format(data.get('end')))

        where = ' and '.join(where)
        vs,total = [],0

        vs = cls.select_vs(cols = cols, where=where, page=page, limit=limit, order=' send_timestamp desc ')
        total = cls.total(where = where )
        send = int(time.time() * 1000)
        slog.debug('select * from %s where %s,total: %s taking:%d ms' % (cls._tbl,where,total,(send - sbegin)))
        return vs, total

    @classmethod
    def ignore_insert_to_db(cls,data):
        return cls.ignore_insert(data = data)

    @classmethod
    def update_insert_to_db(cls,data):
        return cls.update_insert(data = data)

    @classmethod
    def insert_to_db(cls,data):
        return cls.insert(data = data)
    
    @classmethod
    def update_incry(cls,clause):
        print('update table %s: %s ' % (cls._tbl,clause))
        return cls.update(clause = clause)

    @classmethod
    def update_case(cls,data=None, where=''):
        print('update table system_alarm_info_table: %s where:%s' % (json.dumps(data),where))
        return cls.update_dict(data = data, where = where )


# store network_id to network_num relationship 
class NetworkIdNumSql(Bean):
    _tbl = 'network_id_num_table'
    _cols = 'network_num, network_id, network_type'

    def __init__(self):
        return

    @classmethod
    def query_from_db(cls,data,cols = None,page = 1, limit = 200):
        sbegin = int(time.time() * 1000)
        where ,vs,total = [],[],0

        if data.get('network_id'):
            where.append(' `network_id` = "{0}" '.format(data.get('network_id')))

        # network_type choices_list is [rec,zec,edg,arc,adv,val]
        if data.get('network_type'):
            where.append(' `network_type` = "{0}" '.format(data.get('network_type')))

        if data.get('network_num'):
            where.append(' `network_num` = {0} '.format(data.get('network_num')))

        where = ' and '.join(where)
        vs,total = [],0

        vs = cls.select_vs(cols = cols, where=where, page=page, limit=limit, order='')
        total = cls.total(where = where )
        send = int(time.time() * 1000)
        slog.debug('select * from %s where %s,total: %s taking:%d ms' % (cls._tbl,where,total,(send - sbegin)))
        return vs, total

    @classmethod
    def ignore_insert_to_db(cls,data):
        return cls.ignore_insert(data = data)

    @classmethod
    def update_insert_to_db(cls,data):
        return cls.update_insert(data = data)

    @classmethod
    def insert_to_db(cls,data):
        return cls.insert(data = data)
    
    @classmethod
    def update_incry(cls,clause):
        print('update table %s: %s ' % (cls._tbl,clause))
        return cls.update(clause = clause)

    @classmethod
    def update_case(cls,data=None, where=''):
        print('update table network_id_num_table: %s where:%s' % (json.dumps(data),where))
        return cls.update_dict(data = data, where = where )


#  cron job for alarm: cpu、bandwidth...
class SystemCronInfoSql(Bean):
    _tbl = 'system_cron_info_table'
    _cols = 'id,public_ip_port,net1,net2,net3,net4,net5,net6,net7,net8,net9,net10,send_timestamp,cpu,mem,send_bandwidth,recv_bandwidth,send_packet,recv_packet'

    def __init__(self):
        return

    @classmethod
    def query_from_db(cls,data,cols = None,page = 1, limit = 200):
        sbegin = int(time.time() * 1000)
        where ,vs,total = [],[],0

        if data.get('public_ip_port'):
            where.append(' `public_ip_port` = "{0}" '.format(data.get('public_ip_port')))

        # attention: max net size is 10
        for i in range(1,11):
            net_sql_field = 'net{0}'.format(i)  # net1, net2...net10
            if data.get(net_sql_field):
                where.append(' `{0}` = {1} '.format(net_sql_field, data.get(net_sql_field)))

        if data.get('begin'):
            where.append(' `send_timestamp` >= {0} '.format(data.get('begin')))
        if data.get('end'):
            where.append(' `send_timestamp` <= {0} '.format(data.get('end')))

        where = ' and '.join(where)
        vs,total = [],0

        vs = cls.select_vs(cols = cols, where=where, page=page, limit=limit, order=' send_timestamp desc ')
        total = cls.total(where = where )
        send = int(time.time() * 1000)
        slog.debug('select * from %s where %s,total: %s taking:%d ms' % (cls._tbl,where,total,(send - sbegin)))
        return vs, total

    @classmethod
    def ignore_insert_to_db(cls,data):
        return cls.ignore_insert(data = data)

    @classmethod
    def update_insert_to_db(cls,data):
        return cls.update_insert(data = data)

    @classmethod
    def insert_to_db(cls,data):
        return cls.insert(data = data)
    
    @classmethod
    def update_incry(cls,clause):
        print('update table %s: %s ' % (cls._tbl,clause))
        return cls.update(clause = clause)

    @classmethod
    def update_case(cls,data=None, where=''):
        print('update table system_cron_info_table: %s where:%s' % (json.dumps(data),where))
        return cls.update_dict(data = data, where = where )


