#-*-coding:utf8-*-
# app config

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
