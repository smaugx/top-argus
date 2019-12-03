#!/usr/bin/env python
#-*- coding:utf8 -*-

import ipinfo
import json

access_token = '059f319e4984b3'
handler = ipinfo.getHandler(access_token)



def GetIPLocation(ip_address = []):
    result = {}
    if not ip_address:
        return result
    try:
        result = handler.getBatchDetails(ip_address)
    except Exception as e:
        pass
    return result


if __name__ == '__main__':
    ip_address = ['119.167.153.50', '118.193.107.80','197.199.254.2', '197.199.254.3','197.199.254.4', '127.0.0.1']
    result = GetIPLocation(ip_address) 
    print(json.dumps(result, indent = 4))
