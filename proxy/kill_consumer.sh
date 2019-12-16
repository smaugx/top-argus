kill -9 `ps -ef |grep redis_consumer.py |grep -v grep |awk -F ' ' '{print $2}' `
