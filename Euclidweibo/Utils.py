# -*- coding: utf-8 -*-
# @Time    : 2023/3/21 21:35
# @Author  : Euclid-Jie
# @File    : Utils.py
import json

import requests
from bs4 import BeautifulSoup


def Get_json_data(URL, header):
    response = requests.get(URL, headers=header, timeout=60)  # 使用request获取网页
    html = response.content.decode('utf-8', 'ignore')  # 将网页源码转换格式为html
    data_json = json.loads(html)
    return data_json


def Get_soup_data(URl, header):
    response = requests.get(URl, headers=header, timeout=60)  # 使用request获取网页
    html = response.content.decode('utf-8', 'ignore')  # 将网页源码转换格式为html
    soup = BeautifulSoup(html, 'lxml')
    return soup


def remove_upPrintable_chars(s):
    """移除所有不可见字符"""
    return ''.join(x for x in s if x.isprintable())
