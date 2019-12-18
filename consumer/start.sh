source  ../vvlinux/bin/activate

echo $1

python main_consumer.py -t $1
