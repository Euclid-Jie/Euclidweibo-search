# -*- coding: utf-8 -*-
# @Time    : 2023/2/9 23:18
# @Author  : Euclid-Jie
# @File    : Get_longTextContent.py
import json
import requests
from Euclidweibo import Set_header


def Get_longTextContent(data_json):
    if '展开' in data_json['text']:
        URL = 'https://weibo.com/ajax/statuses/longtext?id={}'.format(data_json['mblogid'])
        response = requests.get(URL, headers=Set_header('../cookie.txt'), timeout=60)  # 使用request获取网页
        html = response.content.decode('utf-8', 'ignore')  # 将网页源码转换格式为html
        longTextContent = json.loads(html)['data']['longTextContent']
        data_json['longTextContent'] = longTextContent.encode('gbk', 'ignore').decode('gbk')
    else:
        data_json['longTextContent'] = ''
    return data_json
