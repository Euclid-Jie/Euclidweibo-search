# -*- coding: utf-8 -*-
# @Time    : 2023/2/9 20:06
# @Author  : Euclid-Jie
# @File    : Set_header.py
import os


def Set_header(cookie_path=None):
    """
    设置header内容，可根据自己的更改cookie
    :param cookie_path: cookie path
    :return:
    """
    if cookie_path:
        with open(cookie_path, 'rt', encoding='utf-8') as f:
            cookie = f.read().strip()
        header = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/104.0.0.0 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
                      '*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'Cookie': cookie
        }
    else:
        header = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/104.0.0.0 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
                      '*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
        }
    return header

