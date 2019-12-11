#!/usr/bin/env python
#-*- coding:utf8 -*-

import os
now_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(now_dir)  #parent dir
activate_this = '%s/vvlinux/bin/activate_this.py' % base_dir
exec(open(activate_this).read())

import sys
sys.path.insert(0, base_dir)

import argparse
from werkzeug.security import generate_password_hash, check_password_hash
from database.user_sql import UserInfoSql
from common.slogging import slog

user_info_sql = UserInfoSql()


def add_user(username, password, email = '123@topargus.com'):
    password_hash = generate_password_hash(password)
    data = {
            'username': username,
            'password_hash': password_hash,
            'email': email
            }
    try:
        user_info_sql.insert_to_db(data)
    except Exception as e:
        print('insert username:{0} failed, error:{1}'.format(username, e))
        return

    print('insert username:{0} ok'.format(username))
    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.description='TOP-Argus User-Tool，add/update user'
    parser.add_argument('-u', '--username', help='username', required=True)
    parser.add_argument('-p', '--password', help='password', required=True)
    parser.add_argument('-m', '--mail', help='email', default = '123@topargus.com')
    args = parser.parse_args()

    add_user(args.username, args.password, args.mail)
