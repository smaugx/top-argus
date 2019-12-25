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
                id MEDIUMINT NOT NULL AUTO_INCREMENT,
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
                PRIMARY KEY (id),
                INDEX (chain_hash, send_node_id,send_timestamp)
)
        ENGINE =InnoDB
        DEFAULT CHARSET =utf8;

/* 每一个包对应的收包信息（主要是收包节点ID以及IP)*/
DROP TABLE IF EXISTS packet_recv_info_table;
CREATE TABLE IF NOT EXISTS packet_recv_info_table(
                chain_hash INT(10) unsigned NOT NULL,
                recv_node_id VARCHAR(73) DEFAULT "",
                recv_node_ip VARCHAR(20) DEFAULT "",
                INDEX (chain_hash)
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

/* 用户管理*/
DROP TABLE IF EXISTS user_info_table;
CREATE TABLE IF NOT EXISTS user_info_table(
                username VARCHAR(20) NOT NULL,
                password_hash VARCHAR(100) NOT NULL,
                email  VARCHAR(20) DEFAULT "",
                PRIMARY KEY (username)
)
        ENGINE =InnoDB
        DEFAULT CHARSET =utf8;
