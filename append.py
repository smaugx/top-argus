#!/usr/bin/env python3
# -*- coding:utf8 -*-


import os
import time



def append_log(filename = './xtop.log'):
    F = open(filename, 'a')
    line1 = 'xnetwork-08:35:49.634-T1776:[Keyfo]-(elect_vhost.cc: send:181): original_elect_vhost_send local_node_id:010000fc609372cc194a437ae775bdbf00000000d60a7c10e9cc5f94e24cb9c63ee1fba3 chain_hash:4165143189 chain_msgid:655361 chain_msg_size:9184 send_timestamp:1573547749649 src_node_id:690000010140ff7fffffffffffffffff0000000032eae48d5405ad0a57173799f7490716 dest_node_id:690000010140ff7fffffffffffffffff000000009aee88245d7e31e7abaab1ac9956d5a0 is_root:0 broadcast:0\n'
    line2 = 'xnetwork-08:35:49.385-T1721:[Keyfo]-(elect_vhost.cc: HandleRumorMessage:381): final_handle_rumor local_node_id:010000fc609372cc194a437ae775bdbf00000000d60a7c10e9cc5f94e24cb9c63ee1fba3 chain_hash:1146587997 chain_msgid:917505 packet_size:602 chain_msg_size:189 hop_num:1 recv_timestamp:1573547749394 src_node_id:010000ffffffffffffffffffffffffff0000000088ae064b2bb22948a2aee8ecd81c08f9 dest_node_id:67000000ff7fff7fffffffffffffffff0000000032eae48d5405ad0a57173799f7490716 is_root:0 broadcast:0\n'
    index = 1
    while True:
        if index % 2 == 0:
            F.write(line1)
            print('write1')
        else:
            F.write(line2)
            print('write2')
        time.sleep(0.2)
        index += 1
    F.close()


if __name__ == "__main__":
    append_log()


