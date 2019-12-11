#!/usr/bin/env python
#-*- coding:utf8 -*-


import json
import time
import datetime
import random
import copy
import os
from database.user_sql import UserInfoSql
from common.slogging import slog


class User(object):
    def __init__(self):
        # init db obj
        self.user_info_sql = UserInfoSql()
        return

    def get_user_info(self, data = {}):
        if data == None:
            data = {}
        vs,total = [],0
        vs,total = self.user_info_sql.query_from_db(data, page = None, limit = None)
        if not vs:
            slog.debug('user_info_sql query_from_db failed, data:{0}'.format(json.dumps(data)))
        return vs

