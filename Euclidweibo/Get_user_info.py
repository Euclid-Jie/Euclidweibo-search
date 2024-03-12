# -*- coding: utf-8 -*-
# @Time    : 2023/2/9 20:01
# @Author  : Euclid-Jie
# @File    : Get_user_info.py
from .Set_header import Set_header
import json
import requests
import os

__all__ = ["Get_user_info"]


def Get_user_info(uid):
    """
    base weibo user's uid, get his gender

    future can get user's more detail info

    base url : https://weibo.com/ajax/profile/info?uid=1202150843
    """

    URL = "https://weibo.com/ajax/profile/info?uid={}".format(uid)
    current_dir = os.path.abspath(os.path.dirname(__file__))
    parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
    header = Set_header(os.path.join(parent_dir, "cookie.txt"))
    response = requests.get(URL, headers=header, timeout=60)  # 使用request获取网页
    html = response.content.decode("utf-8", "ignore")  # 将网页源码转换格式为html
    data_json = json.loads(html)["data"]

    return data_json