#user nobody;

worker_processes 2;

error_log  /var/log/nginx/error.log  info;

events{
        worker_connections 1024; 
}


http{
        #设置默认类型为二进制流
        default_type    application/octet-stream;
        include /usr/local/smaug/nginx/conf/mime.types;

        #nginx的HttpLog模块指定，指定nginx日志的输出格式，输出格式为access
        log_format access '$remote_addr - $remote_user [$time_local] "$request" '
                '$status $body_bytes_sent "$http_referer" '
                '"$http_user_agent" "$http_x_forwarded_for"';
        #access日志存在未知
        access_log  /var/log/nginx/access.log   access;
        #开启高效模式文件传输模式，将tcp_nopush和tcp_nodelay两个指另设置为on，用于防止网络阻塞。
        sendfile    on;
        tcp_nopush  on;
        tcp_nodelay on;
        #设置客户端连接保持活动的超时时间
        keepalive_timeout   65;


        upstream mydash{
                 ip_hash;
                 server 192.168.50.242:5000 weight=1;
                 #server 192.168.22.230:8080 weight=1;
                }

        server{
            listen 80;
            server_name 192.168.50.242;
            charset    utf-8; #设置编码为utf-8;

            location /api {
                  proxy_pass http://mydash;
            }

            location / {
                root webapp;
            }

            error_page   500 502 503 504  /50x.html;  

            location = /50x.html {
                root   html;
            }

    }
}
