# -*- coding: utf-8 -*-
# @Time    : 2023/2/9 23:18
# @Author  : Euclid-Jie
# @File    : Get_longTextContent.py
import json
import os

import requests
from .Set_header import Set_header

__all__ = ["Get_longTextContent"]


def Get_longTextContent(data_json, header=None):
    header = Set_header()
    if data_json["isLongText"]:
        URL = "https://weibo.com/ajax/statuses/longtext?id={}".format(
            data_json["mblogid"]
        )
        response = requests.get(URL, headers=header, timeout=60)  # 使用request获取网页
        html = response.content.decode("utf-8", "ignore")  # 将网页源码转换格式为html
        try:
            longTextContent = json.loads(html)["data"]["longTextContent"]
            data_json["longTextContent"] = longTextContent.encode(
                "gbk", "ignore"
            ).decode("gbk")
        except KeyError:
            data_json["longTextContent"] = ""
        except json.decoder.JSONDecodeError:
            data_json["longTextContent"] = ""
    else:
        data_json["longTextContent"] = ""
    return data_json
