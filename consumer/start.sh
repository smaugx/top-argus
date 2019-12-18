source  ../vvlinux/bin/activate

echo $1

nohup python main_consumer.py -t $1 > /dev/null & 2>&1
