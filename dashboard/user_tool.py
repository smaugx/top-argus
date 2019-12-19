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
import random
from werkzeug.security import generate_password_hash, check_password_hash
from database.user_sql import UserInfoSql
from common.slogging import slog

user_info_sql = UserInfoSql()

user_list = [
        'smaug',
        'taylor',
        'justin',
        'tim',
        'blue',
        'hench'
        'aries',
        'evan',
        'rober',
        'helen',
        'asher', 
        'cameo',
        'eason',
        'ernest',
        'freezing',
        'george',
        'hank',
        'jimmy',
        'jufeng',
        'lynch',
        'nathan',
        'payton',
        'rockey',
        'sawyer',
        'tinker',
        'wens',
        'wish',
    ]
        

def generate_password(user):
    pass_word_choice = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',
            ',','$','@','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z',
            '0','1','2','3','4','5','6','7','8','9',
        ]
    password = '{0}_'.format(user)
    for i  in range(0,10):
        c = random.choice(pass_word_choice)
        password += c
    return password

def create_all_user():
    global user_list
    for user in user_list:
        password = generate_password(user)
        print('user:{0} pass:{1}'.format(user, password))
        add_user(user, password)
    return


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
        return False

    print('insert username:{0} ok'.format(username))
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.description='TOP-Argus User-Tool，add/update user'
    parser.add_argument('-u', '--username', help='username')
    parser.add_argument('-p', '--password', help='password')
    parser.add_argument('-m', '--mail', help='email', default = '123@topargus.com')
    parser.add_argument('-a', '--all', help='create all users,should call once', default = 'false')
    args = parser.parse_args()

    if args.all == 'true':
        create_all_user()

    if args.username != None and args.password != None:
        add_user(args.username, args.password, args.mail)
