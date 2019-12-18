kill -9 `ps -ef |grep main_consumer.py |grep -v grep |awk -F ' ' '{print $2}' `
