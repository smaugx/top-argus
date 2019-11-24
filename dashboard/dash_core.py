#!/usr/bin/env python
#-*- coding:utf8 -*-


import json
import time
import queue
import copy
import threading
from database.packet_sql import PacketInfoSql, PacketRecvInfoSql
from common.slogging import slog


class Dash(object):
    def __init__(self):
        # init db obj
        self.packet_info_sql = PacketInfoSql()
        self.packet_recv_info_sql = PacketRecvInfoSql()

    def get_packet_info(self, data):
        vs,total = [],0
        vs,total = self.packet_info_sql.query_from_db(data)
        if not vs:
            slog.debug('packet_info_sql query_from_db failed, data:{0}'.format(json.dumps(data)))
        return vs,total

    def get_packet_recv_info(self, data):
        vs,total = [],0
        vs,total = self.packet_recv_info_sql.query_from_db(data)
        if not vs:
            slog.debug('packet_recv_info_sql query_from_db failed, data:{0}'.format(json.dumps(data)))
        return vs,total
        

