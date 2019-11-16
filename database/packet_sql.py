# -*- coding:utf-8 -*-
from database.bean import Bean
import time
import json

class PacketInfoSql(Bean):
    _tbl = 'packet_info_table'  #所有发包收包信息发在一个表中
    _cols = 'id,chain_hash,chain_msgid,chain_msg_size,packet_size,send_timestamp,is_root,broadcast,send_node_id,src_node_id,dest_node_id,recv_nodes_num,hop_num,taking,timestamp'

    def __init__(self):
        return

    #TODO 增加 timestamp 范围
    #name is something like 'bepo retry';priority is list,different from __init__()
    #def query(cls,id ,gid , service_name , type  ,name ,priority ,page = 1, limit = 50):
    @classmethod
    def query_from_db(cls,data,page = 1, limit = 50):
        where ,vs,total = [],[],0

        if data.get('id'):
            where.append(' `id` = "{0}" '.format(data.get('id')))

        if data.get('gid'):
            where.append(' gid = "{0}" '.format(data.get('gid')))

        if data.get('service_name'):
            where.append(' service_name = "{0}" '.format(data.get('service_name')))

        if data.get('type'):
            where.append(' `type` like "{0}"'.format(data.get('type')))

        if data.get('name') :
            namelist = data.get('name').split(' ')
            wn = []
            for n in namelist:
                if not n: 
                    continue
                #e.g: name = 'bepo rery'，results include in 'bepo' and 'retry'
                wn.append(' name like "%%{0}%%" '.format(n))
            wn = ' and '.join(wn)
            wn = ' ( {0} )'.format(wn)
            where.append(wn)


        if data.get('priority'): 
            wp = []
            for p in data.get('priority'):
                if int(p) not in [0,1,2,3,4,5]:
                    continue
                #e.g priority = [1,2] ,results include in 1 or 2
                wp.append(' priority = %d ' % int(p))
            wp = ' or '.join(wp)
            wp = ' ( {0} )'.format(wp)
            where.append(wp)

        where = ' and '.join(where)
        vs,total = [],0
        vs = cls.select_vs(where=where, page=page, limit=limit, order=' priority ,update_at desc ')
        total = cls.total(where = where )
        print('select * from %s where %s,total: %s' % ('main_event_cases',where,total))
        return vs, total

    @classmethod
    def uniq_insert_to_db(cls,data):
        return cls.uniq_insert(data = data)

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
    _cols = 'chain_hash,recv_node_id,recv_node_ip'

    def __init__(self):
        return

    #TODO 增加 timestamp 范围
    #name is something like 'bepo retry';priority is list,different from __init__()
    #def query(cls,id ,gid , service_name , type  ,name ,priority ,page = 1, limit = 50):
    @classmethod
    def query_from_db(cls,data,page = 1, limit = 50):
        where ,vs,total = [],[],0

        if data.get('id'):
            where.append(' `id` = "{0}" '.format(data.get('id')))

        if data.get('gid'):
            where.append(' gid = "{0}" '.format(data.get('gid')))

        if data.get('service_name'):
            where.append(' service_name = "{0}" '.format(data.get('service_name')))

        if data.get('type'):
            where.append(' `type` like "{0}"'.format(data.get('type')))

        if data.get('name') :
            namelist = data.get('name').split(' ')
            wn = []
            for n in namelist:
                if not n: 
                    continue
                #e.g: name = 'bepo rery'，results include in 'bepo' and 'retry'
                wn.append(' name like "%%{0}%%" '.format(n))
            wn = ' and '.join(wn)
            wn = ' ( {0} )'.format(wn)
            where.append(wn)


        if data.get('priority'): 
            wp = []
            for p in data.get('priority'):
                if int(p) not in [0,1,2,3,4,5]:
                    continue
                #e.g priority = [1,2] ,results include in 1 or 2
                wp.append(' priority = %d ' % int(p))
            wp = ' or '.join(wp)
            wp = ' ( {0} )'.format(wp)
            where.append(wp)

        where = ' and '.join(where)
        vs,total = [],0
        vs = cls.select_vs(where=where, page=page, limit=limit, order=' priority ,update_at desc ')
        total = cls.total(where = where )
        print('select * from %s where %s,total: %s' % ('main_event_cases',where,total))
        return vs, total

    @classmethod
    def uniq_insert_to_db(cls,data):
        return cls.uniq_insert(data = data)

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

