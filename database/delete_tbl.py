#!/usr/bin/env python 
#-*- coding:utf8 -*-
import MySQLdb
import config

argus_alarm_db_cfg = {
        "DB_HOST": config.ARGUS_ALARM_DB_HOST,
        "DB_PORT": config.ARGUS_ALARM_DB_PORT,
        "DB_USER": config.ARGUS_ALARM_DB_USER,
        "DB_PASS": config.ARGUS_ALARM_DB_PASS,
        "DB_NAME": config.ARGUS_ALARM_DB_NAME,
}

#TODO
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
    except Exception, e:
        print 'connect db failed:%s' % e
        return None


def delete_table(service_name):
  if not service_name:
    return
  db = connect_db(argus_alarm_db_cfg)
  cursor = db.cursor()

  sqla = 'drop table %s_events' % service_name
  sqlb = 'drop table %s_event_groups' % service_name
  cursor.execute(sqla)
  cursor.execute(sqlb)
  cursor.close()
  return

if __name__ == "__main__":
  service_list = ['Marco','BearCache','SSD','speed_detect','hogback']
  for s in service_list:
    delete_table(s)
