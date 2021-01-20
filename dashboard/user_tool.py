#!/usr/bin/env python
#-*- coding:utf8 -*-

import os,sys
project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(project_path))


import argparse
import random
from werkzeug.security import generate_password_hash, check_password_hash
from database.user_sql import UserInfoSql

user_info_sql = UserInfoSql()

user_data_file = './user.data'
user_list = [
        'smaug',
        'taylor',
        'justin',
        'tim',
        'blue',
        'hench',
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

def create_all_user_with_file(filename):
    global user_data_file

    user_data_list = []
    if os.path.exists(filename):
        with open(filename, 'r') as fin:
            for line in fin:
                print(line)
                if line.startswith('#') or line.startswith('$'):
                    continue
                if line.endswith('\n'):
                    line = line[:-1]
                sp = line.split(' ')
                if len(sp) != 2:
                    print("filed error in {0}, line eg:\nsomeusername somepassword".format(user_data_file))
                    continue
                username = sp[0]
                password = sp[1]
                print('parse username:{0} password:{1}'.format(username, password))
                user_data_list.append([username, password])
            fin.close()
    else:
        print('{0} not exist'.format(filename))

    for item in user_data_list:
        print('will create username:{0} password:{1}'.format(item[0], item[1]))
        add_user(item[0], item[1])

    return


def create_all_user_with_randompass():
    global user_list, user_data_file
    user_data_list = []
    for user in user_list:
        password = generate_password(user)
        print('user:{0} pass:{1}'.format(user, password))
        add_user(user, password)
        user_data_list.append([user, password])

    with open(user_data_file, 'w') as fout:
        for item in user_data_list:
            line = '{0} {1}\n'.format(item[0], item[1])
            fout.write(line)
        fout.close()

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
    parser.add_argument('-f', '--filename', help='create all users from filename', default = '')
    args = parser.parse_args()

    if args.all == 'true':
        create_all_user_with_randompass()
        sys.exit(0)

    if args.filename:
        create_all_user_with_file(args.filename)
        sys.exit(0)

    if args.username != None and args.password != None:
        add_user(args.username, args.password, args.mail)
