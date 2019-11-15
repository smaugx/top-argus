# -*- coding:utf-8 -*-
from database.bean import Bean
from database.store import argus_alarm_db
import time
import json

#评论系统
class Comments(Bean): 
  _db = argus_alarm_db
  _tbl = 'comments'  #table name
  _cols = 'id,parentid,username,msg,timestamp,type,groupid'   

  def __init__(self,row = [],comment = {}):
    self.timestamp = None

    if comment:
      timestamp = int(comment.get('timestamp'))
      now = time.time()
      if abs(now - timestamp) > 5 * 60:
        timestamp = now
      tl = time.localtime(timestamp)
      date = time.strftime('%Y-%m-%d %H:%M:%S', tl)
      self.timestamp        = date


    if row:
      keys = self._cols.split(',')
      comment = dict(zip(keys,row))
      self.timestamp  = comment.get('timestamp')

    self.id         = comment.get('id')
    self.parentid   = comment.get('parentid')
    self.username   = comment.get('username')
    self.msg        = comment.get('msg')
    self.type       = comment.get('type')
    self.groupid    = comment.get('groupid')


  def to_dict(self,timeformat = False):
    comment = {}
    comment['id']               = self.id
    comment['parentid']         = self.parentid
    comment['username']         = self.username
    comment['msg']              = self.msg
    comment['type']             = self.type
    comment['timestamp']        = self.timestamp
    comment['groupid']          = self.groupid
    if timeformat:
      comment['timestamp'] = int(time.mktime(time.strptime(str(self.timestamp),'%Y-%m-%d %H:%M:%S')))

    return comment

  @classmethod
  def query_from_db(cls, data ,page = 1, limit = 500):
    vs,total,where = [],0, []

    if data.get('id'):
      where.append(' `id` = "{0}" '.format(data.get('id')))

    if data.get('parentid'):
      where.append(' parentid = "{0}" '.format(data.get('parentid')))

    if data.get('username'):
      where.append(' username = "{0}" '.format(data.get('username')))

    if data.get('msg') :
      messages = data.get('msg').split(' ') #用于评论查找
      wm = []
      for m in messages:
        if not m: 
          continue
        #e.g: msg = 'ctn down'，results include in 'ctn' and 'down'
        wm.append(' msg like "%%{0}%%" '.format(n))
      wm = ' and '.join(wm)
      wm = ' ( {0} ) '.format(wm)
      where.append(wm)
    
    order = ' id '
    if data.get('latest'):
      order += ' desc'
      limit = int(data.get('latest'))

    if int(data.get('offset')) > 0:
      page = data.get('offset')

    if data.get('withbulk') != None:
      if int(data.get('withbulk')) == 0:
        where.append(' `type` <>  "bulk_status" and `type` <> "bulk_processor" ')

    where = ' and '.join(where)
    try:
      vs = cls.select_vs(where=where, page=page, limit=limit, order= order)
      total = cls.total(where = where )
      print 'select * from %s where %s,total: %s' % ('comments',where,total)
    except Exception as e:
      print 'select * from %s where %s error: %s' % ('comments',where,e)

    return vs, total


  @classmethod
  def insert_to_db(cls,data):
    print "insert to table comments:%s" % json.dumps(data)
    return cls.insert(data = data)



#用户管理
class Users(Bean): 
  _db = argus_alarm_db
  _tbl = 'users'  #table name
  _cols = 'username,alias,groupname,phone,im,weixin,service,mail,finished_tasks,unfinished_tasks,role,subscription'   

  #def __init__(self,username = None,alias = None,phone = None,im = None,weixin = None,mail = None,\
  #    finished_tasks = None,unfinished_tasks = None,role = None,subscription = None,user = {}):
  def __init__(self,row = [],user = {}):
    if row:
      keys = self._cols.split(',')
      user = dict(zip(keys,row))

    self.username          = user.get('username')
    self.alias             = user.get('alias')
    self.groupname         = user.get('groupname')
    self.phone             = user.get('phone')
    self.im                = user.get('im')
    self.weixin            = user.get('weixin')
    self.service           = user.get('service')
    self.mail              = user.get('mail')
    self.finished_tasks    = user.get('finished_tasks')
    self.unfinished_tasks  = user.get('unfinished_tasks')
    self.role              = user.get('role')
    self.subscription      = user.get('subscription')

  def to_dict(self):
    user = {}
    user['username']           = self.username
    user['alias']              = self.alias
    user['groupname']          = self.groupname
    user['phone']              = self.phone
    user['im']                 = self.im
    user['weixin']             = self.weixin 
    user['service']            = self.service
    user['mail']               = self.mail
    user['finished_tasks']     = self.finished_tasks
    user['unfinished_tasks']   = self.unfinished_tasks
    user['role']               = self.role
    user['subscription']       = self.subscription
    return user


  @classmethod
  def query_from_db(cls, data):
    vs,total,where = [],0, []

    if data.get('username'):
      where.append(' `username`  = "{0}" '.format(data.get('username')))

    if data.get('groupname'):
      where.append(' groupname like "{0}" '.format(data.get('groupname')))

    if data.get('service'):
      where.append(' service like "%%{0}%%" '.format(data.get('service')))

    if data.get('role') != None:
      where.append(' role like "{0}" '.format(data.get('role')))

    where = ' and '.join(where)
    try:
      vs = cls.select_vs(where=where)
      total = cls.total(where = where )
    except Exception as e:
      print 'select * from %s where %s error: %s' % ('users',where,e)
      vs,total = [],-1

    return vs, total


  
  @classmethod
  def update_db(cls,data=None, where=''):
    print 'update table %s: %s where:%s' % ('users',json.dumps(data),where)
    return cls.update_dict(data = data, where = where )
 

  @classmethod
  def insert_to_db(cls,data):
    return cls.insert(data = data)

  def save(self):
    user = self.to_dict()
    
    vs,total = self.query_from_db(data = {'username':self.username})
    if total > 0:
      where = ' `username` = "%s"' % self.username
      self.update_db(data = user,where = where)
    else:
      self.insert_to_db(user)



#告警记录
class Notice(Bean):
  _db = argus_alarm_db
  _tbl = 'notice'  #table name
  _cols = 'id,caseid,groupid,groupname,service_name,type,to_user,channel,status,timestamp'   

  def __init__(self,row = [],notice = {}):
    self.timestamp = None

    if notice:
      timestamp = int(notice.get('timestamp'))
      now = time.time()
      if abs(now - timestamp) > 5 * 60:
        timestamp = now
      tl = time.localtime(timestamp)
      date = time.strftime('%Y-%m-%d %H:%M:%S', tl)
      self.timestamp        = date

    if row:
      notice = {}
      keys = self._cols.split(',')
      notice = dict(zip(keys,row))
      self.timestamp  = notice.get('timestamp')

    self.id            =   notice.get('id')
    self.caseid        =   notice.get('caseid')
    self.groupid       =   notice.get('groupid')
    self.groupname     =   notice.get('groupname')
    self.service_name  =   notice.get('service_name')
    self.type          =   notice.get('type')
    self.to_user       =   notice.get('to_user')
    self.channel       =   notice.get('channel')
    self.status        =   notice.get('status')


  def to_dict(self,timeformat = False):
    notice = {}
    notice['id']           =  self.id
    notice['caseid']       =  self.caseid
    notice['groupid']      =  self.groupid
    notice['groupname']    =  self.groupname
    notice['service_name'] =  self.service_name
    notice['type']         =  self.type
    notice['to_user']      =  self.to_user
    notice['channel']      =  self.channel
    notice['status']       =  self.status
    notice['timestamp']    =  self.timestamp
    if timeformat:
      notice['timestamp'] = int(time.mktime(time.strptime(str(self.timestamp),'%Y-%m-%d %H:%M:%S')))

    return notice 

  def save(self):
    notice = self.to_dict()
    self.insert(data = notice)

  @classmethod
  def query_from_db(cls, data):
    vs,total,where = [],0, []

    if data.get('caseid'):
      where.append(' `caseid`  = "{0}" '.format(data.get('caseid')))

    if data.get('groupid'):
      where.append(' `groupid` = "{0}" '.format(data.get('groupid')))

    if data.get('service_name'):
      where.append(' service_name like "%%{0}%%" '.format(data.get('service_name')))

    if data.get('type'):
      where.append(' type = "{0}" '.format(data.get('type')))

    wh = []
    if data.get('hostname') :
      for h in data.get('hostname'):
        if not h:
          continue
        wh.append(' groupname like "%%{0}%%" '.format(h))   #TODO make sure operate 'and' or 'or'
      wh  = ' and '.join(wh)
      wh  = ' ( {0} )'.format(wh)
      where.append(wh)

    wu = []
    if data.get('to_user') :
      for u in data.get('to_user'):
        if not u:
          continue
        wu.append(' `to_user` like "%%{0}%%" '.format(u))
      wu  = ' or '.join(wu)
      wu  = ' ( {0} )'.format(wu)
      where.append(wu)


    if data.get('channel'):
      where.append(' `channel` like "{0}" '.format(data.get('to_user')))

    where = ' and '.join(where)
    try:
      vs = cls.select_vs(where=where)
      total = cls.total(where = where )
    except Exception as e:
      print 'select * from %s where %s error: %s' % ('users',where,e)
      vs,total = [],-1

    return vs, total



