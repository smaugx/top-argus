
# MariaDB（Mysql)
[Centos 7安装配置MariaDB](https://blog.csdn.net/toubennuhai/article/details/70808610)

# Redis

```
yum install redis -y
which redis-cli

# 启动 Redis
mkdir /usr/local/redis -p
cd /usr/local/redis/
cp /etc/redis*.conf .
# 根据需要修改 redis 参数,比如 配置密码： requirepass smaug_redis_123 ; bind 0.0.0.0
 redis-server  ./redis.conf  &
 
 # 验证 redis-server 启动是否成功
 redis-cli  -a smaug_redis_123
```

# Nginx

## 编译安装
[nginx服务器详细安装过程](https://segmentfault.com/a/1190000007116797)

```
yum -y install gcc gcc-c++ make libtool zlib zlib-devel openssl openssl-devel pcre pcre-devel

mkdir /root/temp -p && cd /root/temp
wget http://nginx.org/download/nginx-1.14.2.tar.gz
tar zxvf nginx-1.14.2.tar.gz
cd nginx-1.14.2
./configure --prefix=/usr/local/smaug/nginx --with-http_stub_status_module --with-http_ssl_module --with-pcre
make -j4 && make install
```

## 直接复制 top-argus/web/nginx 目录安装

具体往下看


# top-argus
## 克隆项目
```
# 安装 git 为了克隆项目
yum install -y git

mkdir /root/smaug -p
cd /root/smaug
git clone https://github.com/smaugx/top-argus.git
```

## 依赖安装

```
mkdir -p /root/temp
cd /root/temp && curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3 get-pip.py

which pip

# 可能需要
ln -s /usr/local/bin/pip /usr/bin/pip

# 安装 virtualenv
pip3 install virtualenv

cd /root/smaug/top-argus && virtualenv  -p /usr/bin/python3 vvlinux
source  vvlinux/bin/activate
pip install -r requirements.txt

# 配置文件拷贝
cp common/test_config.py common/config.py

# 测试虚拟环境是否正常
cd dashboard
python dash.py

# 启动正常说明环境配置基本正确，下一步初始化数据库

```

## nginx 安装（已安装则忽略）

```
# 复制 nginx
mkdir -p /usr/local/smaug/
cd /root/smaug/top-argus/web
cp -rf nginx /usr/local/smaug/

# 验证安装
cd /usr/local/smaug/nginx
./sbin/nginx -h

```


## 初始化数据库，创建数据表

```
cd /root/smaug/top-argus/database/mysql

# 创建数据库
mysql -u root -p < create_db_topargus.sql 
  
# 创建数据表
mysql -u root -p < create_db_tables.sql 


# 检查数据库情况 （看到下面的输出表示正常）
MariaDB [(none)]> use topargus;
Database changed
MariaDB [topargus]> show tables;
Empty set (0.00 sec)

MariaDB [topargus]> show tables;
+------------------------+
| Tables_in_topargus     |
+------------------------+
| network_info_table     |
| packet_drop_info_table |
| packet_info_table      |
| packet_recv_info_table |
+------------------------+
4 rows in set (0.00 sec)
```

## Gunicorn运行与配置(已安装则忽略）

```
# 安装
pip install gunicorn
gunicorn -h
```



## 使用 gunicorn 运行 dashboard

```
# 使用 gunicorn 运行 dashboard(注意：均在虚拟环境下进行）

cd /root/smaug/top-argus/dashboard
# 运行
gunicorn -c gunicorn.config dash:app
# 验证 （能看到 Hellow, World)
curl http://0.0.0.0:8080
由于配置了 basic auth，上面可能会看到如下的输出：
# > Unauthorized Access


# db 中创建用户以及用户密码

# 使用 user_tool.py 创建用户以及设置密码，可以先用 -h 查看支持选项
python user_tool.py  -h
python user_tool.py -u [user] -p [password]
# 创建成功会输出 “insert username:smaug ok”

# 再次验证 dashboard 启动是否成功
curl --user user:password http://0.0.0.0:8080 
# 成功后会输出 "user, Hello, World!"
# 注意上述替换成之前在数据库里添加的用户和密码
```

**以上把  dashboard 运行成功后，接下来结合 nginx 进行部署**

## nginx 配置

```
# nginx conf 配置
cd /usr/local/smaug/nginx/
rm -rf conf
cp -rf /root/smaug/top-argus/web/nginx/conf .
cp -rf /root/smaug/top-argus/web/nginx/webapp .

# 修改 listen port 为 80
# 修改 upstream 地址为 127.0.0.1:8080
# nginx 配置验证
mkdir /var/log/nginx/ -p
# 配置文件语法检查
./sbin/nginx  -t
# 启动或者重启
./sbin/nginx
./sbin/nginx -s reload


# 验证(使用已经存在的 user 和 password)
curl --user user:password http://0.0.0.0:80
```

上述配置之后，使用 ngxin 作为前置代理，反向代理到本地的 dash flask，接下来可以使用浏览器进行访问验证，能看到网站已经成型了。

![](./topargus_index.png)
![](./topargus_packet.png)
![](./topargus_about.png)

**可以看到，网站配置正确，但还没有采集数据。下一步就是部署agent ，采集上报数据**。

**至此，前端 dashboard 模块搭建完成， 下一步部署 proxy. 可以部署在同一台机器或者不同的机器上.**


## 运行 proxy

```
# 均在 virtualenv 环境下操作
cd /root/smaug/top-argus/proxy
python proxy.py


# 验证 （能看到Hello, World)
curl http://0.0.0.0:9091

# 启动 nginx ，使用 nginx 代理 proxy
gunicorn -c gunicorn.config proxy:app
cd /usr/local/smaug/nginx/
./sbin/nginx

# 验证
curl http://0.0.0.0:9090
```


**至此，已经把 proxy 搭建安装完成。 根据实际情况， dashboard 和 proxy 可以位于一台机器上。**

**注意实际情况下，需要修改 /root/smaug/top-argus/common/config.py 里面的 redis host 和 mysql host.**

# agent 部署
上面的步骤已经把 proxy 和 dash 运行起来了，其中

+ proxy:  为 agent 采集数据进行上报的目标对象，负责整理分析数据存盘；
+ dash: web 查询界面

**首先我们找到一台机器，作为部署的机器，一般是一台跳板机。然后以此跳板机对 agent 部署与运维**。

```
# 克隆 top-argus-deploy 项目，并准备好 ansible host 文件
git clone https://github.com/smaugx/top-argus-deploy.git
tar zcvf top-argus-deploy.tar.gz top-argus-deploy

# 用 ansible 传输 tar.gz 到各个目标机器
ansible -i smhost  all -m copy -a "src=./top-argus-deploy.tar.gz dest=/home/topuser/"

# 解压缩并安装，为启动 agent 做准备
ansible -i smhost  all -m shell -a "cd /home/topuser && tar zxvf top-argus-deploy.tar.gz && cd top-argus-deploy && sh install.sh"

# 启动 agent (替换成正确的 proxy host 以及 xtop.log绝对路径）
ansible -i smhost  all -m shell -a "cd /home/topuser/top-argus-deploy && sh start.sh 127.0.0.1:9090 ./xtop.log"

# 停止 agent
ansible -i smhost  all -m shell -a "cd /home/topuser/top-argus-deploy && sh stop.sh"

# 重启 agent
ansible -i smhost  all -m shell -a "cd /home/topuser/top-argus-deploy && sh restart.sh 127.0.0.1:9090 ./xtop.log"    

```

# consumer 部署
consumer 是消费者集群，消费上报的报警日志，分析并存盘。

按照上述的环境配置把虚拟环境安装完成之后：

```

cd /root/smaug/top-argus/common
# 修改正确的 redis db host 

cd /root/smaug/top-argus/consumer
source  ../vvlinux/bin/activate
sh start.sh all
```


## 激动人心啊
![](./topargusindex.png)
![](./toparguspacket.png)



# 一键重置并重启 top-argus
前提：如果上述环境已经安装完成并且成功启动了 top-argus，后续如果有重置的需求，那么需要用到下面的脚本:

功能：

+ 重置 top-argus 所有数据（清除 db 和相关缓存文件）
+ 重启 top-argus(proxy,dash,consumer)


[topargus.sh](https://github.com/smaugx/top-argus/blob/master/topargus.sh)

```
$ ./topargus.sh
```
