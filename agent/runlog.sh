cd /root/smaug/top-argus/

source ./vvlinux/bin/activate

cd ./agent

nohup python logwatch.py  /tmp/rec1/xtop.log > /dev/null & 2>&1
nohup python logwatch.py  /tmp/rec2/xtop.log > /dev/null & 2>&1
nohup python logwatch.py  /tmp/rec3/xtop.log > /dev/null & 2>&1
nohup python logwatch.py  /tmp/rec4/xtop.log > /dev/null & 2>&1
nohup python logwatch.py  /tmp/rec5/xtop.log > /dev/null & 2>&1
nohup python logwatch.py  /tmp/rec6/xtop.log > /dev/null & 2>&1
nohup python logwatch.py  /tmp/rec7/xtop.log > /dev/null & 2>&1

nohup python logwatch.py  /tmp/zec1/xtop.log > /dev/null & 2>&1
nohup python logwatch.py  /tmp/zec2/xtop.log > /dev/null & 2>&1
nohup python logwatch.py  /tmp/zec3/xtop.log > /dev/null & 2>&1
nohup python logwatch.py  /tmp/zec4/xtop.log > /dev/null & 2>&1

nohup python logwatch.py  /tmp/adv1/xtop.log > /dev/null & 2>&1
nohup python logwatch.py  /tmp/adv2/xtop.log > /dev/null & 2>&1
nohup python logwatch.py  /tmp/adv3/xtop.log > /dev/null & 2>&1
nohup python logwatch.py  /tmp/adv4/xtop.log > /dev/null & 2>&1
nohup python logwatch.py  /tmp/adv5/xtop.log > /dev/null & 2>&1
nohup python logwatch.py  /tmp/adv6/xtop.log > /dev/null & 2>&1
nohup python logwatch.py  /tmp/adv7/xtop.log > /dev/null & 2>&1
nohup python logwatch.py  /tmp/adv8/xtop.log > /dev/null & 2>&1
nohup python logwatch.py  /tmp/adv9/xtop.log > /dev/null & 2>&1

nohup python logwatch.py  /tmp/con1/xtop.log > /dev/null & 2>&1
nohup python logwatch.py  /tmp/con2/xtop.log > /dev/null & 2>&1
nohup python logwatch.py  /tmp/con3/xtop.log > /dev/null & 2>&1
nohup python logwatch.py  /tmp/con4/xtop.log > /dev/null & 2>&1
nohup python logwatch.py  /tmp/con5/xtop.log > /dev/null & 2>&1
nohup python logwatch.py  /tmp/con6/xtop.log > /dev/null & 2>&1
nohup python logwatch.py  /tmp/con7/xtop.log > /dev/null & 2>&1
nohup python logwatch.py  /tmp/con8/xtop.log > /dev/null & 2>&1
nohup python logwatch.py  /tmp/con9/xtop.log > /dev/null & 2>&1

nohup python logwatch.py  /tmp/arc1/xtop.log > /dev/null & 2>&1
nohup python logwatch.py  /tmp/arc2/xtop.log > /dev/null & 2>&1

nohup python logwatch.py  /tmp/edge/xtop.log > /dev/null & 2>&1
