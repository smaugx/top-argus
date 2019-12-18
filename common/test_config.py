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
        'global_sample_rate': 50,  # sample_rate%
        'alarm_pack_num': 2,   # upload alarm size one time
        'grep_broadcast': {
            'start': 'true',
            'sample_rate': 10,
            'alarm_type': 'packet',
            'network_focus_on': ['660000', '680000', '690000', '670000'], # src or dest
            'network_ignore':   ['650000'],  # src or dest
            },
        'grep_point2point': {
            'start': 'false',
            'sample_rate': 10,
            'alarm_type': 'packet',
            'network_focus_on': ['660000', '680000', '690000'], # src or dest
            'network_ignore':   ['670000'],  # src or dest
            },
        'grep_networksize': {
            'start': 'true',
            'sample_rate': 5,
            'alarm_type': 'networksize',
            'network_focus_on': ['660000', '680000', '690000'], # src or dest
            'network_ignore':   ['670000'],  # src or dest
            },
        'grep_xtopchain': {
            'start': 'true',
            'alarm_type': 'progress',
            },
        }

