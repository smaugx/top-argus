/*创建数据库*/
/*
CREATE DATABASE topargus 
  DEFAULT CHARACTER SET utf8
  DEFAULT COLLATE utf8_general_ci;
*/
USE topargus;
SET NAMES utf8;

/* 所有发包收包信息统计*/
DROP TABLE IF EXISTS packet_info_table;
CREATE TABLE IF NOT EXISTS packet_info_table(
                uniq_chain_hash BIGINT(20) unsigned NOT NULL,
                chain_hash INT(10) unsigned NOT NULL,
                chain_msgid INT(10) unsigned NOT NULL,
                chain_msg_size INT(10) unsigned DEFAULT 0,
                packet_size INT(10) unsigned DEFAULT 0,
                send_timestamp bigint(20) unsigned DEFAULT 0,
                is_root INT(1) unsigned  DEFAULT 0,
                broadcast INT(1) unsigned DEFAULT 1,
                send_node_id VARCHAR(73) DEFAULT "",
                src_node_id VARCHAR(73) DEFAULT "",
                dest_node_id VARCHAR(73) DEFAULT "",
                dest_networksize int(10) DEFAULT 0,
                recv_nodes_num INT(10) DEFAULT 0,
                hop_num VARCHAR(255) DEFAULT "",
                taking VARCHAR(255) DEFAULT "",
                timestamp Timestamp NOT NULL,
                PRIMARY KEY (uniq_chain_hash),
                INDEX (chain_hash, send_node_id,send_timestamp)
)
        ENGINE =InnoDB
        DEFAULT CHARSET =utf8;

/* 每一个包对应的收包信息（主要是收包节点ID以及IP)*/
DROP TABLE IF EXISTS packet_recv_info_table;
CREATE TABLE IF NOT EXISTS packet_recv_info_table(
                uniq_chain_hash BIGINT(20) unsigned NOT NULL,
                recv_node_id VARCHAR(73) DEFAULT "",
                recv_node_ip VARCHAR(20) DEFAULT "",
                INDEX (uniq_chain_hash)
)
        ENGINE =InnoDB
        DEFAULT CHARSET =utf8;


/* 每一个 network_id 对应的节点以及 ip*/
DROP TABLE IF EXISTS network_info_table;
CREATE TABLE IF NOT EXISTS network_info_table(
                network_id VARCHAR(20) NOT NULL,
                network_info MEDIUMTEXT DEFAULT "",
                PRIMARY KEY (network_id)
)
        ENGINE =InnoDB
        DEFAULT CHARSET =utf8;


/* 网络丢包率*/
DROP TABLE IF EXISTS packet_drop_info_table;
CREATE TABLE IF NOT EXISTS packet_drop_info_table(
                network_id VARCHAR(20) NOT NULL,
                timestamp bigint(20) unsigned DEFAULT 0,
                drop_rate float(5,1) DEFAULT 0.0,
                INDEX (network_id)
)
        ENGINE =InnoDB
        DEFAULT CHARSET =utf8;


/* 节点信息*/
DROP TABLE IF EXISTS node_info_table;
CREATE TABLE IF NOT EXISTS node_info_table(
                public_ip_port VARCHAR(25) NOT NULL,
                root VARCHAR(73) DEFAULT "", 
                status VARCHAR(10) DEFAULT "online", /* offline */
                rec  VARCHAR(1000) DEFAULT "",
                zec  VARCHAR(1000) DEFAULT "",
                edg  VARCHAR(1000) DEFAULT "",
                arc  VARCHAR(1000) DEFAULT "",
                adv  VARCHAR(1000) DEFAULT "",
                val  VARCHAR(1000) DEFAULT "",
                PRIMARY KEY (public_ip_port),
                INDEX (root,status)
)
        ENGINE =InnoDB
        DEFAULT CHARSET =utf8;

/* 系统事件，具有比较高的优先级的事件*/
DROP TABLE IF EXISTS system_alarm_info_table;
CREATE TABLE IF NOT EXISTS system_alarm_info_table(
                id INT(10) unsigned NOT NULL AUTO_INCREMENT,
                priority  INT(10)  unsigned DEFAULT 0,   /* priority high with high value */
                public_ip_port VARCHAR(25) NOT NULL, 
                root VARCHAR(73) DEFAULT "", 
                alarm_info VARCHAR(1000) DEFAULT "",
                send_timestamp bigint(20) unsigned DEFAULT 0,
                PRIMARY KEY (id),
                INDEX (priority, public_ip_port, root, send_timestamp)
)
        ENGINE =InnoDB
        DEFAULT CHARSET =utf8;

/*
   网络id 到数字的映射，从 1 开始递增
*/
DROP TABLE IF EXISTS network_id_num_table;
CREATE TABLE IF NOT EXISTS network_id_num_table(
                network_num INT(10) unsigned NOT NULL AUTO_INCREMENT,
                network_id VARCHAR(20) NOT NULL,
                network_type VARCHAR(3) NOT NULL, /* rec/zec/edg/arc/adv/val */
                PRIMARY KEY (network_num),
                INDEX (network_id,network_type)
)
        ENGINE =InnoDB
        DEFAULT CHARSET =utf8;

/* 
  为了标识每一条上报信息来源节点所属的网络，支持最大到 10 号网络;
  即一个节点最多支持同时有 10 种角色, 表字段默认最大添加标记 10 种网络，格式为 net[x]，其中 x 范围 [1,10], 比如 net1, net2...net10;
  最大支持 10 种网络的原因是： 1 rec + 1 zec + 1 edg + 1 arc + 2 adv + 4 val;
  注意，如果网络规模超过 10 个，则会出错，实际使用时一般不会配置这么多（超过10） 的网络;
*/

/* 系统定时采集信息, 比如 cpu/bandwidth 等*/
DROP TABLE IF EXISTS system_cron_info_table;
CREATE TABLE IF NOT EXISTS system_cron_info_table(
                id INT(10) unsigned NOT NULL AUTO_INCREMENT,
                public_ip_port VARCHAR(25) NOT NULL,
                net1   INT(1) unsigned DEFAULT 0, /* 0 is not in this network, 1 is in this network */
                net2   INT(1) unsigned DEFAULT 0, /* 0 is not in this network, 1 is in this network */
                net3   INT(1) unsigned DEFAULT 0, /* 0 is not in this network, 1 is in this network */
                net4   INT(1) unsigned DEFAULT 0, /* 0 is not in this network, 1 is in this network */
                net5   INT(1) unsigned DEFAULT 0, /* 0 is not in this network, 1 is in this network */
                net6   INT(1) unsigned DEFAULT 0, /* 0 is not in this network, 1 is in this network */
                net7   INT(1) unsigned DEFAULT 0, /* 0 is not in this network, 1 is in this network */
                net8   INT(1) unsigned DEFAULT 0, /* 0 is not in this network, 1 is in this network */
                net9   INT(1) unsigned DEFAULT 0, /* 0 is not in this network, 1 is in this network */
                net10  INT(1) unsigned DEFAULT 0, /* 0 is not in this network, 1 is in this network */
                send_timestamp bigint(20) unsigned DEFAULT 0, /* cron job, min step usually 1 min */
                cpu INT(3)  unsigned DEFAULT 0,  /* % */
                mem INT(3)  unsigned DEFAULT 0,  /* % */
                send_bandwidth INT(10)  unsigned DEFAULT 0,  /* Kb/s */
                recv_bandwidth INT(10)  unsigned DEFAULT 0,  /* Kb/s */
                send_packet INT(10)  unsigned DEFAULT 0,
                recv_packet INT(10)  unsigned DEFAULT 0,
                PRIMARY KEY (id),
                INDEX (public_ip_port,net1,net2,net3,net4,net5,net6,net7,net8,net9,net10,send_timestamp)
)
        ENGINE =InnoDB
        DEFAULT CHARSET =utf8;

