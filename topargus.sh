#/bin/bash

echo_and_run() { echo "$*" ; "$@" ; }

cd /root/smaug/top-argus/
pwd
source  vvlinux/bin/activate

echo "kill proxy"
echo_and_run echo 'ps -ef |grep  proxy:app |grep -v grep |awk -F ' ' '{print $2}' |xargs kill -9' | bash
sleep 1


echo "kill dash"
echo_and_run echo 'ps -ef |grep  dash:app |grep -v grep |awk -F ' ' '{print $2}' |xargs kill -9' | bash
sleep 1


echo "kill consumer"
echo_and_run echo 'ps -ef |grep  main_consumer |grep -v grep |awk -F ' ' '{print $2}' |xargs kill -9' | bash
sleep 1

echo "will reset database"
echo_and_run echo 'cd /root/smaug/top-argus/database/mysql && mysql -uroot -P3306 --password="smaug"  < reset.sql' | bash
echo "reset database done"
sleep 1

echo_and_run echo 'rm -f /tmp/.topargus_iplocation' | bash
sleep 1

echo_and_run echo 'rm -f /dev/shm/topargus_gconfig' | bash
sleep 1

echo_and_run echo 'rm -f /dev/shm/topargus_network_info' | bash
sleep 1

echo '###################################'
echo ''
echo "reset data done, will start dash/proxy/consumer"
echo ''

echo "start dash"
echo_and_run echo 'cd /root/smaug/top-argus/dashboard/ && gunicorn -c gunicorn.config dash:app' | bash
sleep 1

echo 'start proxy'
echo_and_run echo 'cd /root/smaug/top-argus/proxy && gunicorn -c gunicorn.config proxy:app' | bash
sleep 1

echo 'start consumer'
echo_and_run echo 'cd /root/smaug/top-argus/consumer && nohup python3 main_consumer.py -t all  -e docker > /dev/null  2>&1 &' | bash
sleep 1


echo ""
echo "###########################"
echo  "reset finished"
echo ""
