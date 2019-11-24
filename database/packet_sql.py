# -*- coding:utf-8 -*-
from database.bean import Bean
import time
import json
from common.slogging import slog

class PacketInfoSql(Bean):
    _tbl = 'packet_info_table'  #所有发包收包信息发在一个表中
    _cols = 'id,chain_hash,chain_msgid,chain_msg_size,packet_size,send_timestamp,is_root,broadcast,send_node_id,src_node_id,dest_node_id,dest_networksize,recv_nodes_num,hop_num,taking,timestamp'

    def __init__(self, data):
        slog.info('PacketInfoSql init')
        return

    #TODO 增加 timestamp 范围
    #name is something like 'bepo retry';priority is list,different from __init__()
    #def query(cls,id ,gid , service_name , type  ,name ,priority ,page = 1, limit = 50):
    @classmethod
    def query_from_db(cls,data,page = 1, limit = 50):
        where ,vs,total = [],[],0

        if data.get('id'):
            where.append(' `id` = "{0}" '.format(data.get('id')))

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
            if len(data.get('src_node_id')) <= 10:
                where.append(' src_node_id regexp "{0}" '.format(data.get('src_node_id')))
            else:
                where.append(' src_node_id = "{0}" '.format(data.get('src_node_id')))

        if data.get('dest_node_id'):
            if len(data.get('dest_node_id')) <= 10:
                where.append(' dest_node_id regexp "{0}" '.format(data.get('dest_node_id')))
            else:
                where.append(' dest_node_id = "{0}" '.format(data.get('dest_node_id')))

        where = ' and '.join(where)
        vs,total = [],0
        vs = cls.select_vs(where=where, page=page, limit=limit, order=' timestamp desc ')
        total = cls.total(where = where )
        slog.debug('select * from %s where %s,total: %s' % (cls._tbl,where,total))
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

    def __init__(self,data):
        return

    #TODO 增加 timestamp 范围
    #name is something like 'bepo retry';priority is list,different from __init__()
    #def query(cls,id ,gid , service_name , type  ,name ,priority ,page = 1, limit = 50):
    @classmethod
    def query_from_db(cls,data,page = 1, limit = 50):
        where ,vs,total = [],[],0

        if data.get('chain_hash'):
            where.append(' chain_hash = {0} '.format(data.get('chain_hash')))

        if data.get('recv_node_id'):
            if len(data.get('recv_node_id')) <= 10:
                where.append(' recv_node_id regexp "{0}" '.format(data.get('recv_node_id')))
            else:
                where.append(' recv_node_id = "{0}" '.format(data.get('recv_node_id')))

        if data.get('recv_node_ip'):
            if len(data.get('recv_node_ip')) <= 10:
                where.append(' recv_node_ip regexp "{0}" '.format(data.get('recv_node_ip')))
            else:
                where.append(' recv_node_ip = "{0}" '.format(data.get('recv_node_ip')))

        where = ' and '.join(where)
        vs,total = [],0
        vs = cls.select_vs(where=where, page=page, limit=limit, order='')
        total = cls.total(where = where )
        slog.debug('select * from %s where %s,total: %s' % (cls._tbl,where,total))
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

