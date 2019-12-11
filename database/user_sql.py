# -*- coding:utf-8 -*-
from database.bean import Bean
import time
import json
from common.slogging import slog

# user_info 
class UserInfoSql(Bean):
    _tbl = 'user_info_table'
    _cols = 'username, password_hash, email'

    def __init__(self):
        return

    @classmethod
    def query_from_db(cls,data,page = None, limit = None):
        where ,vs,total = [],[],0

        if data.get('username'):
            where.append(' `username` = "{0}" '.format(data.get('username')))
        if data.get('email'):
            where.append(' `email` = "{0}" '.format(data.get('email')))

        where = ' and '.join(where)
        vs,total = [],0
        vs = cls.select_vs(where = where, page = None, limit = None, order = None)
        total = cls.total(where = where )
        slog.debug('select * from %s where %s,total: %s' % (cls._tbl,where,total))
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
