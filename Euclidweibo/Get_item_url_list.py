# -*- coding: utf-8 -*-
# @Time    : 2023/2/9 20:42
# @Author  : Euclid-Jie
# @File    : Get_item_url_list.py
import re
import os
import requests_html
from .Set_proxies import Set_proxies
from .Set_header import Set_header

__all__ = ["Get_item_url_list"]


def Get_item_url_list(URL, proxies):
    """
    get all single weibo item 's url, just like https://weibo.com/1310272120/MrOtA75Fd
    1310272120 is uid
    MrOtA75Fd is mblogid
    use this mblogid, we get https://weibo.com/ajax/statuses/show?id=MrOtA75Fd
    con get all info about the single weibo
    """
    session = requests_html.HTMLSession()
    current_dir = os.path.abspath(os.path.dirname(__file__))
    parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
    header = Set_header(os.path.join(parent_dir, "cookie.txt"))
    proxies = Set_proxies(proxies)
    if proxies:
        if "127.0.0.1" not in list(proxies.values())[0]:
            proxies = None
    response = session.get(URL, headers=header, proxies=proxies)
    response.encoding = "utf-8"
    all_url_list = list(response.html.links)
    url_list = []
    pat = re.compile("\d{10}/[A-Za-z0-9]{9}")
    for url in all_url_list:
        tag = pat.findall(url)
        if tag:
            url_list.append(tag[0])

    return url_list
