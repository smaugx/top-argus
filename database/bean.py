# -*- coding:utf-8 -*-
__author__ = 'Smaugx'
from database.store import topargus_alarm_db
#from database.s import topargus_alarm_db

class Bean(object):
    _tbl = ''    #table name
    _cols = ''
    _db = topargus_alarm_db

    @classmethod
    def insert(cls, data=None):
        if not data:
            raise ValueError('argument data is invalid')

        size = len(data)
        keys = data.keys()
        safe_keys = ['`%s`' % k for k in keys]
        sql = 'INSERT INTO `%s`(%s) VALUES(%s)' % (cls._tbl, ','.join(safe_keys), '%s' + ',%s' * (size - 1))
        print(sql)
        last_id = cls._db.insert(sql, [data[key] for key in keys])
        return last_id

    @classmethod
    def ignore_insert(cls, data=None):
        if not data:
            raise ValueError('argument data is invalid')

        size = len(data)
        keys = data.keys()
        safe_keys = ['`%s`' % k for k in keys]
        # ignore PRIMARY KEY Duplicate
        sql = 'INSERT IGNORE INTO `%s`(%s) VALUES(%s)' % (cls._tbl, ','.join(safe_keys), '%s' + ',%s' * (size - 1))
        print(sql)
        last_id = cls._db.insert(sql, [data[key] for key in keys])
        return last_id

    @classmethod
    def update_insert(cls, data=None):
        if not data:
            raise ValueError('argument data is invalid')

        size = len(data)
        keys = data.keys()
        safe_keys = ['`%s`' % k for k in keys]
        # ignore PRIMARY KEY Duplicate
        sql = 'REPLACE INTO `%s`(%s) VALUES(%s)' % (cls._tbl, ','.join(safe_keys), '%s' + ',%s' * (size - 1))
        print(sql)
        last_id = cls._db.insert(sql, [data[key] for key in keys])
        return last_id

    @classmethod
    def delete(cls, where=None ):
        sql = 'DELETE FROM `%s`' % cls._tbl
        if not where:
            return cls._db.update(sql)

        sql += ' WHERE ' + where
        return cls._db.update(sql)

    @classmethod
    def update(cls, clause=None,params = None):
        sql = 'UPDATE `%s` SET %s' % (cls._tbl, clause)
        print(sql,clause)
        return cls._db.update(sql ,params)

    @classmethod
    def update_dict(cls, data=None, where=''):
        if not data:
            raise ValueError('argument data is invalid')

        size = len(data)
        keys = data.keys()
        safe_keys = ['`%s`' % k for k in keys]
        values = [data[key] for key in keys]
        arr = ['%s=%%s' % key for key in safe_keys]
        if not where:
            return cls.update(','.join(arr) ,values)
        else:
            return cls.update(', '.join(arr) + ' WHERE ' + where,values)

    @classmethod
    def select(cls, cols=None, where=None, order=None, limit=None, page=None, offset=None):
        if cols is None:
            cols = cls._cols

        sql = 'SELECT %s FROM `%s`' % (cols, cls._tbl)

        if where:
            sql = '%s WHERE %s' % (sql, where)

        if order:
            sql = '%s ORDER BY %s' % (sql, order)

        if limit is not None:
            sql = '%s LIMIT %s' % (sql, limit)

        if offset is not None:
            sql = '%s OFFSET %s' % (sql, offset)

        if page is not None:
            offset = (int(page) - 1) * int(limit)
            if offset < 0:
                offset = 0
            sql = '%s OFFSET %s' % (sql, offset)

        return cls._db.query_all(sql )

    @classmethod
    def select_vs(cls, where=None, order=None, limit=None, page=None, offset=None):
        rows = cls.select(where=where, order=order, limit=limit, page=page, offset=offset)
        return rows

    @classmethod
    def read(cls, where=None):
        vs = cls.select_vs(where=where)
        if vs:
            return vs[0]
        else:
            return None

    @classmethod
    def column(cls, col=None, where=None,  order=None, limit=None, page=None, offset=None):
        rows = cls.select(col, where, order, limit, page, offset)
        return [row[0] for row in rows]

    @classmethod
    def total(cls, where=None ):
        sql = 'SELECT COUNT(1) FROM `%s`' % cls._tbl
        if not where:
            ret = cls._db.query_column(sql)
            return ret[0]
        sql += ' WHERE ' + where
        ret = cls._db.query_column(sql )
        return ret[0]

    @classmethod
    def exists(cls, where=None ):
        return cls.total(where ) > 0
