sh ./stop.sh
sleep 1

if [ ! $1 ]; then
  echo "param invalid"
  exit
else
  echo "param is:" $1
  sh ./start.sh $1
fi

