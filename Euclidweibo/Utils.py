# -*- coding: utf-8 -*-
# @Time    : 2023/3/21 21:35
# @Author  : Euclid-Jie
# @File    : Utils.py
import json

import requests


def Get_json_data(URL, header):
    response = requests.get(URL, headers=header, timeout=60)  # 使用request获取网页
    html = response.content.decode('utf-8', 'ignore')  # 将网页源码转换格式为html
    data_json = json.loads(html)
    return data_json
