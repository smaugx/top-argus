pwd

mkdir ./deploy_agent -p
rm -rf ./deploy_agent/*

cp -rf agent  ./deploy_agent
cp -rf common ./deploy_agent
mkdir -p ./deploy_agent/vvlinux

rm -f deploy_agent.tar.gz
tar zcvf deploy_agent.tar.gz  ./deploy_agent

rm -rf  ./deploy_agent

