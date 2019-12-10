cd /root/smaug/top-argus/

source ./vvlinux/bin/activate

cd ./agent
pwd

nohup python argus_agent.py -a 127.0.0.1:9090 -f /tmp/rec1/xtop.log > /dev/null & 2>&1
nohup python argus_agent.py -a 127.0.0.1:9090 -f /tmp/rec2/xtop.log > /dev/null & 2>&1
nohup python argus_agent.py -a 127.0.0.1:9090 -f /tmp/rec3/xtop.log > /dev/null & 2>&1
nohup python argus_agent.py -a 127.0.0.1:9090 -f /tmp/rec4/xtop.log > /dev/null & 2>&1
nohup python argus_agent.py -a 127.0.0.1:9090 -f /tmp/rec5/xtop.log > /dev/null & 2>&1
nohup python argus_agent.py -a 127.0.0.1:9090 -f /tmp/rec6/xtop.log > /dev/null & 2>&1
nohup python argus_agent.py -a 127.0.0.1:9090 -f /tmp/rec7/xtop.log > /dev/null & 2>&1

nohup python argus_agent.py -a 127.0.0.1:9090 -f /tmp/zec1/xtop.log > /dev/null & 2>&1
nohup python argus_agent.py -a 127.0.0.1:9090 -f /tmp/zec2/xtop.log > /dev/null & 2>&1
nohup python argus_agent.py -a 127.0.0.1:9090 -f /tmp/zec3/xtop.log > /dev/null & 2>&1
nohup python argus_agent.py -a 127.0.0.1:9090 -f /tmp/zec4/xtop.log > /dev/null & 2>&1

nohup python argus_agent.py -a 127.0.0.1:9090 -f /tmp/adv1/xtop.log > /dev/null & 2>&1
nohup python argus_agent.py -a 127.0.0.1:9090 -f /tmp/adv2/xtop.log > /dev/null & 2>&1
nohup python argus_agent.py -a 127.0.0.1:9090 -f /tmp/adv3/xtop.log > /dev/null & 2>&1
nohup python argus_agent.py -a 127.0.0.1:9090 -f /tmp/adv4/xtop.log > /dev/null & 2>&1
nohup python argus_agent.py -a 127.0.0.1:9090 -f /tmp/adv5/xtop.log > /dev/null & 2>&1
nohup python argus_agent.py -a 127.0.0.1:9090 -f /tmp/adv6/xtop.log > /dev/null & 2>&1
nohup python argus_agent.py -a 127.0.0.1:9090 -f /tmp/adv7/xtop.log > /dev/null & 2>&1
nohup python argus_agent.py -a 127.0.0.1:9090 -f /tmp/adv8/xtop.log > /dev/null & 2>&1
nohup python argus_agent.py -a 127.0.0.1:9090 -f /tmp/adv9/xtop.log > /dev/null & 2>&1

nohup python argus_agent.py -a 127.0.0.1:9090 -f /tmp/con1/xtop.log > /dev/null & 2>&1
nohup python argus_agent.py -a 127.0.0.1:9090 -f /tmp/con2/xtop.log > /dev/null & 2>&1
nohup python argus_agent.py -a 127.0.0.1:9090 -f /tmp/con3/xtop.log > /dev/null & 2>&1
nohup python argus_agent.py -a 127.0.0.1:9090 -f /tmp/con4/xtop.log > /dev/null & 2>&1
nohup python argus_agent.py -a 127.0.0.1:9090 -f /tmp/con5/xtop.log > /dev/null & 2>&1
nohup python argus_agent.py -a 127.0.0.1:9090 -f /tmp/con6/xtop.log > /dev/null & 2>&1
nohup python argus_agent.py -a 127.0.0.1:9090 -f /tmp/con7/xtop.log > /dev/null & 2>&1
nohup python argus_agent.py -a 127.0.0.1:9090 -f /tmp/con8/xtop.log > /dev/null & 2>&1
nohup python argus_agent.py -a 127.0.0.1:9090 -f /tmp/con9/xtop.log > /dev/null & 2>&1

nohup python argus_agent.py -a 127.0.0.1:9090 -f /tmp/arc1/xtop.log > /dev/null & 2>&1
nohup python argus_agent.py -a 127.0.0.1:9090 -f /tmp/arc2/xtop.log > /dev/null & 2>&1

nohup python argus_agent.py -a 127.0.0.1:9090 -f /tmp/edge/xtop.log > /dev/null & 2>&1
