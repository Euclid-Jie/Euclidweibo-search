# -*- coding: utf-8 -*-
# @Time    : 2023/2/9 21:36
# @Author  : Euclid-Jie
# @File    : Get_single_weibo_data.py
import json

import requests
from Euclidweibo import *


def Get_single_weibo_data(mblogid, header):
    """
    get single weibo's data by weibo_url, just like https://weibo.com/1310272120/MrOtA75Fd
    which can get by using Get_item_url_list.py

    in fact get https://weibo.com/ajax/statuses/show?id=MrOtA75Fd
    con help to simplify works

    Attention: If need full content text, another get is needed https://weibo.com/ajax/statuses/longtext?id=MrOtA75Fd

    data contains:
        text: weibo content with some html
        text_raw: weibo content
        region_name: province

        attitudes_count = data['attitudes_count']
        comments_count = data['comments_count']
        reposts_count = data['reposts_count']

        mid: a id correspond to this weibo
        created_at: the time created this weibo
        source: the specific device information, just like "Phone 14 Pro"
        screen_name: the user who created this weibo
        ......
    """
    URL = 'https://weibo.com/ajax/statuses/show?id={}'.format(mblogid)
    response = requests.get(URL, headers=header, timeout=60)  # 使用request获取网页
    html = response.content.decode('utf-8', 'ignore')  # 将网页源码转换格式为html
    data_json = json.loads(html)
    if '展开' in data_json['text']:
        URL = 'https://weibo.com/ajax/statuses/longtext?id={}'.format(mblogid)
        response = requests.get(URL, headers=header, timeout=60)  # 使用request获取网页
        html = response.content.decode('utf-8', 'ignore')  # 将网页源码转换格式为html
        longTextContent = json.loads(html)['data']['longTextContent']
        data_json['longTextContent'] = longTextContent.encode('gbk', 'ignore').decode('gbk')
    else:
        data_json['longTextContent'] = ''
    return data_json


if __name__ == '__main__':
    data = Get_single_weibo_data(mblogid='MrOtA75Fd', header=Set_header('../cookie.txt'))
    part_data = {
        'time': data['created_at'],
        'mid': data['mid'],
        'nick_name': data['user']['screen_name'],
        'attitudes_count': data['attitudes_count'],
        'comments_count': data['comments_count'],
        'reposts_count': data['reposts_count'],
        'text': data['text'],
        'text_raw': data['text_raw'],
        'longTextContent': data['longTextContent']
    }
    print(part_data)
