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
                send_timestamp INT(13) unsigned DEFAULT 0,
                is_root INT(1) unsigned  DEFAULT 0,
                broadcast INT(1) unsigned DEFAULT 1,
                send_node_id VARCHAR(73) DEFAULT "",
                src_node_id VARCHAR(73) DEFAULT "",
                dest_node_id VARCHAR(73) DEFAULT "",
                recv_nodes_num INT(10) DEFAULT 0,
                hop_num VARCHAR(255) DEFAULT "",
                taking VARCHAR(255) DEFAULT "",
                timestamp Timestamp NOT NULL,
                PRIMARY KEY (chain_hash),
                INDEX (id,send_node_id,timestamp)
)
        ENGINE =InnoDB
        DEFAULT CHARSET =utf8;

/* 每一个包对应的收包信息（主要是收包节点ID以及IP)*/
DROP TABLE IF EXISTS packet_recv_info_table;
CREATE TABLE IF NOT EXISTS packet_recv_info_table(
                chain_hash INT(10) unsigned NOT NULL,
                recv_nodes_id VARCHAR(20) DEFAULT "",
                recv_nodes_ip VARCHAR(20) DEFAULT "",
                PRIMARY KEY (chain_hash)
)
        ENGINE =InnoDB
        DEFAULT CHARSET =utf8;
