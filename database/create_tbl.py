#!/usr/bin/env python 
#-*- coding:utf8 -*-
import MySQLdb
import config

TOPARGUS_alarm_db_cfg = {
        "DB_HOST": config.TOPARGUS_ALARM_DB_HOST,
        "DB_PORT": config.TOPARGUS_ALARM_DB_PORT,
        "DB_USER": config.TOPARGUS_ALARM_DB_USER,
        "DB_PASS": config.TOPARGUS_ALARM_DB_PASS,
        "DB_NAME": config.TOPARGUS_ALARM_DB_NAME,
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

def create_groups_table(service_name):
  if not service_name:
    return
  db = connect_db(TOPARGUS_alarm_db_cfg)
  cursor = db.cursor()
  cursor.execute("SET sql_notes = 0; ")
  # create db here....

  group_sql = """DROP TABLE IF EXISTS %s_event_groups;
  CREATE TABLE IF NOT EXISTS %s_event_groups(
  id MEDIUMINT NOT NULL AUTO_INCREMENT,
  parentid VARCHAR(50) ,
  gid VARCHAR(50) NOT NULL,
  groupname VARCHAR(512) NOT NULL,        
  total_count INT(10) unsigned DEFAULT 0,         
  status int(3) unsigned DEFAULT 0,
  assigned_processor VARCHAR(64) ,
  deadline Timestamp NULL DEFAULT NULL,
  timestamp Timestamp,
  update_at Timestamp NULL DEFAULT NULL,
  mark VARCHAR(1024) DEFAULT NULL,
  response_time Timestamp NULL DEFAULT NULL,
  repair_time  Timestamp  NULL DEFAULT NULL,
  PRIMARY KEY (id),
  INDEX(parentid,gid,groupname,timestamp),
  FOREIGN KEY (parentid) REFERENCES main_event_cases(id)
          ON DELETE CASCADE
          ON UPDATE CASCADE
  )
  ENGINE =InnoDB
  DEFAULT CHARSET =utf8;"""   % (service_name,service_name)

  cursor.execute(group_sql)
  cursor.close()
  return

def create_events_table(service_name):
  if not service_name:
    return
  db = connect_db(TOPARGUS_alarm_db_cfg)
  cursor = db.cursor()
  cursor.execute("SET sql_notes = 0; ")

  event_sql = """DROP TABLE IF EXISTS %s_events;
  CREATE TABLE IF NOT EXISTS %s_events(
  id MEDIUMINT NOT NULL AUTO_INCREMENT,
  parentid MEDIUMINT ,
  gid VARCHAR(50) NOT NULL,
  callback VARCHAR(255),
  hostname VARCHAR(255) NOT NULL,
  tag  VARCHAR(255) ,
  step INT(10)  unsigned DEFAULT 1,
  value VARCHAR(1024) DEFAULT NULL,
  status int(3) unsigned DEFAULT 0,
  timestamp Timestamp,
  PRIMARY KEY (id),
  INDEX(parentid,gid,hostname,timestamp),
  FOREIGN KEY (parentid) REFERENCES %s_event_groups(id)
  ON DELETE CASCADE
  ON UPDATE CASCADE
  )
  ENGINE =InnoDB
  DEFAULT CHARSET =utf8;"""  % (service_name,service_name,service_name)


  cursor.execute(event_sql)
  cursor.close()
  return

def create(service_name):
  error = None
  try:
    create_groups_table(service_name)
    create_events_table(service_name)
  except Exception as e:
    error = 'create sql table failed of %s,error:%s' % (service_name,e)
  return error


if __name__ == "__main__":
  service_name = 'hellotest'
  error = create(service_name)
  print error
