# -*- coding: utf-8 -*-
# @Time    : 2023/2/9 23:18
# @Author  : Euclid-Jie
# @File    : Get_longTextContent.py
import json
import os

import requests
from Euclidweibo import Set_header


def Get_longTextContent(data_json, header=None):
    if header is None:
        current_dir = os.path.abspath(os.path.dirname(__file__))
        parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
        header = Set_header(os.path.join(parent_dir, 'cookie.txt'))
    if '展开' in data_json['text']:
        URL = 'https://weibo.com/ajax/statuses/longtext?id={}'.format(data_json['mblogid'])
        response = requests.get(URL, headers=header, timeout=60)  # 使用request获取网页
        html = response.content.decode('utf-8', 'ignore')  # 将网页源码转换格式为html
        try:
            longTextContent = json.loads(html)['data']['longTextContent']
            data_json['longTextContent'] = longTextContent.encode('gbk', 'ignore').decode('gbk')
        except KeyError:
            data_json['longTextContent'] = ''
        except json.decoder.JSONDecodeError:
            data_json['longTextContent'] = ''
    else:
        data_json['longTextContent'] = ''
    return data_json
