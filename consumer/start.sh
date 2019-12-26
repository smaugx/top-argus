source  ../vvlinux/bin/activate


if [ ! $1 ]; then
  echo "param invalid"
  exit
else
  echo "param is:" $1
  nohup python main_consumer.py -t $1  -e docker > /dev/null & 2>&1
fi


