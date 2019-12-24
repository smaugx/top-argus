#-*- coding:utf-8 -*-
#import MySQLdb
import common.config as config
import pymysql.cursors
import time


topargus_alarm_db_cfg = {
        "DB_HOST": config.TOPARGUS_ALARM_DB_HOST,
        "DB_PORT": config.TOPARGUS_ALARM_DB_PORT,
        "DB_USER": config.TOPARGUS_ALARM_DB_USER,
        "DB_PASS": config.TOPARGUS_ALARM_DB_PASS,
        "DB_NAME": config.TOPARGUS_ALARM_DB_NAME,
}


# Connect to the database
def py_connect_db(cfg):
  conn = pymysql.connect(
  host=cfg['DB_HOST'],
  port=cfg['DB_PORT'],
  user=cfg['DB_USER'],
  passwd=cfg['DB_PASS'],
  db=cfg['DB_NAME'],
  use_unicode=True,
  charset="utf8",
  connect_timeout = 200,
  read_timeout = 60,
  cursorclass=pymysql.cursors.DictCursor)
  return conn

def connect_db(cfg):
    try:
        conn = MySQLdb.connect(
            host=cfg['DB_HOST'],
            port=cfg['DB_PORT'],
            user=cfg['DB_USER'],
            passwd=cfg['DB_PASS'],
            db=cfg['DB_NAME'],
            use_unicode=True,
            charset="utf8")
        return conn
    except Exception as e:
        print('connect db failed:%s' % e)
        return None


class DB(object):
    def __init__(self, cfg):
        self.config = cfg
        self.conn = None

    def get_conn(self):
        return py_connect_db(self.config)
        if self.conn is None:
            self.conn = py_connect_db(self.config)
        return self.conn

    def execute(self, *a, **kw):
        cursor = kw.pop('cursor', None)
        #try:
        #cursor = cursor or self.get_conn().cursor()
        conn  = self.get_conn()
        cursor = conn.cursor()
        cursor.execute(*a, **kw)
        conn.commit()
        '''
        #except (AttributeError, MySQLdb.OperationalError):
        except Exception as e :
            self.conn and self.conn.close()
            self.conn = None
            cursor = self.get_conn().cursor()
            cursor.execute(*a, **kw)
        '''
        return cursor

    # insert one record in a transaction
    # return last id
    def insert(self, *a, **kw):
        cursor = None
        #try:
        cursor = self.execute(*a, **kw)
        row_id = cursor.lastrowid
        #self.commit()
        return row_id
        '''
        #except MySQLdb.IntegrityError:
        except Exception as e :
            self.rollback()
        finally:
            #cursor and cursor.close()
            cursor 
        '''

    # update in a transaction
    # return affected row count
    def update(self, *a, **kw):
        cursor = None
        #try:
        cursor = self.execute(*a, **kw)
        row_count = cursor.rowcount
        return row_count
        #except MySQLdb.IntegrityError:
        '''
        except Exception as e :
            self.rollback()
        finally:
            cursor and cursor.close()
        '''
        #cursor and cursor.close()
        cursor 

    def query_all(self, *a, **kw):
        tnow = int(time.time() * 1000)
        cursor = None
        try:
            cursor = self.execute(*a, **kw)
            return cursor.fetchall()
        finally:
            #cursor and cursor.close()
            cursor 
            tend = int(time.time() * 1000)
            print('sql taking:{0} ms'.format(tend - tnow))

    def query_one(self, *a, **kw):
        rows = self.query_all(*a, **kw)
        if rows:
            return rows[0]
        else:
            return None

    def query_column(self, *a, **kw):
        rows = self.query_all(*a, **kw)
        if rows:
            return [list(row.values())[0] for row in rows]
        else:
            return []

    def commit(self):
        return
        '''
        if self.conn:
            try:
                self.conn.commit()
            #except MySQLdb.OperationalError:
            except Exception as e :
                self.conn = None
        '''

    def rollback(self):
        if self.conn:
            try:
                self.conn.rollback()
            #except MySQLdb.OperationalError:
            except Exception as e :
                self.conn = None


topargus_alarm_db = DB(topargus_alarm_db_cfg)
