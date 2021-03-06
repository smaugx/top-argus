#-*-coding:utf8-*-
# app config

# in production environment:        mv test_config.py config.py 

# log set
# log level: debug/info/warn/error/critical
LOGLEVEL = 'debug'

# alarm database
# TODO: read from api instead of db
TOPARGUS_ALARM_DB_HOST = "127.0.0.1"
TOPARGUS_ALARM_DB_PORT = 3306
TOPARGUS_ALARM_DB_USER = "root"
TOPARGUS_ALARM_DB_PASS = "smaug"
TOPARGUS_ALARM_DB_NAME = "topargus"

# i18n
BABEL_DEFAULT_LOCALE   = 'zh_CN'
BABEL_DEFAULT_TIMEZONE = 'Asia/Shanghai'
# aviliable translations
LANGUAGES   = {
    'en':  'English',
    'zh_CN':  'Chinese-Simplified',
}

# redis config
REDIS_HOST = "127.0.0.1"
REDIS_PORT = "6379"
REDIS_PASS = "smaug_redis_123"

# for alarm proxy
SHM_GCONFIG_FILE = '/dev/shm/topargus_gconfig'

PROXY_CONFIG = {
        'global_sample_rate': 500,  # sample_rate%。 50%
        'alarm_pack_num': 2,   # upload alarm size one time
        'config_update_time': 5 * 60,  # 5mins
        'grep_broadcast': {
            'start': 'true',
            'sample_rate': 100,   #10%
            'alarm_type': 'packet',
            'network_focus_on': ['ff0000010000','ff0000020000', 'ff00000f0101', 'ff00000e0101', 'ff00000001'], # src or dest: rec;zec;edg;arc;aud/val
            'network_ignore':   [],  # src or dest
            },
        'grep_point2point': {
            'start': 'false',
            'sample_rate': 10,  #1%
            'alarm_type': 'packet',
            'network_focus_on': ['ff0000010000','ff0000020000', 'ff00000f0101', 'ff00000e0101', 'ff00000001'], # src or dest: rec;zec;edg;arc;aud/val
            'network_ignore':   [],  # src or dest
            },
        'grep_networksize': {
            'start': 'true',
            'sample_rate': 50,  #5%
            'alarm_type': 'networksize',
            },
        'system_cron': {
            'start': 'true',
            'alarm_type': 'system',
            },
        }

