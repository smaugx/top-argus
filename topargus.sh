#/bin/bash

cd /root/smaug/top-argus/
pwd
source  vvlinux/bin/activate

echo "kill proxy"
echo 'ps -ef |grep  proxy:app |grep -v grep |awk -F ' ' '{print $2}' |xargs kill -9'
ps -ef |grep  proxy:app |grep -v grep |awk -F ' ' '{print $2}' |xargs kill -9
sleep 1


echo "kill dash"
echo 'ps -ef |grep  dash:app |grep -v grep |awk -F ' ' '{print $2}' |xargs kill -9'
ps -ef |grep  dash:app |grep -v grep |awk -F ' ' '{print $2}' |xargs kill -9
sleep 1


echo "kill consumer"
echo 'ps -ef |grep  main_consumer |grep -v grep |awk -F ' ' '{print $2}' |xargs kill -9'
ps -ef |grep  main_consumer |grep -v grep |awk -F ' ' '{print $2}' |xargs kill -9
sleep 1

echo "will reset database"
echo 'cd /root/smaug/top-argus/database/mysql && mysql -uroot -P3306 --password="smaug"  < reset.sql'
cd /root/smaug/top-argus/database/mysql && mysql -uroot -P3366 --password="smaug"  < reset.sql
echo "reset database done"
sleep 1

echo 'rm -f /tmp/.topargus_iplocation'
rm -f /tmp/.topargus_iplocation
sleep 1

echo 'rm -f /dev/shm/topargus_gconfig'
rm -f /dev/shm/topargus_gconfig
sleep 1

echo 'rm -f /dev/shm/topargus_network_info'
rm -f /dev/shm/topargus_network_info
sleep 1

echo '###################################'
echo ''
echo "reset data done, will start dash/proxy/consumer"
echo ''

echo "start dash"
echo 'cd /root/smaug/top-argus/dashboard/ && gunicorn -c gunicorn.config dash:app'
cd /root/smaug/top-argus/dashboard/ && gunicorn -c gunicorn.config dash:app
sleep 1

echo 'start proxy'
echo 'cd /root/smaug/top-argus/proxy && gunicorn -c gunicorn.config proxy:app'
cd /root/smaug/top-argus/proxy && gunicorn -c gunicorn.config proxy:app
sleep 1

echo 'start consumer'
echo 'cd /root/smaug/top-argus/consumer && nohup python3 main_consumer.py -t all  -e docker > /dev/null  2>&1 &'
cd /root/smaug/top-argus/consumer && nohup python3 main_consumer.py -t all  -e docker > /dev/null  2>&1 &
sleep 1


echo ""
echo "###########################"
echo  "reset finished"
echo ""
