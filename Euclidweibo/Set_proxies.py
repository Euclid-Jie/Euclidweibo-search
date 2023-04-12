# -*- coding: utf-8 -*-
# @Time    : 2023/4/12 10:06
# @Author  : Euclid-Jie
# @File    : Set_proxies.py

import requests


def Set_proxies(proxies=True, http='http://127.0.0.1', port=12345):
    if proxies:
        IP = '{}:{}'.format(http, port)
        return {'http': IP, 'https': IP}
