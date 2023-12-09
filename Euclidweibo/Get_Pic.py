# -*- coding: utf-8 -*-
# @Time    : 2023/4/18 12:09
# @Author  : Euclid-Jie
# @File    : Get_Pic.py
import os
import requests
import urllib3

header = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/104.0.0.0 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,"
    "*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "referer": "https://weibo.com/",
}


def request_pic(pic_id: str, max_try_times=100):
    try_times = 0
    while try_times < max_try_times:
        try:
            res = requests.get("https://wx2.sinaimg.cn/mw690/{}".format(pic_id), header)
            return res
        # except ConnectionResetError or requests.exceptions.ChunkedEncodingError or urllib3.exceptions.ProtocolError:
        except:
            try_times += 1
    raise TimeoutError("重试{}后仍无效".format(max_try_times))


def path_clear(subFolder: str, FileName):
    """
    get the full folder path and full file path
    :return:
    """
    if "\\" in subFolder:
        FullFolderPath = os.getcwd() + subFolder
    else:
        FullFolderPath = os.getcwd() + "\\" + subFolder
    if not os.path.exists(FullFolderPath):
        os.mkdir(FullFolderPath)

    FullFilePath = os.path.join(FullFolderPath, FileName)
    return FullFilePath


def Get_Pic(pic_id_list: list, root_name: str, subFolder: str = None):
    res_yield = (request_pic(pic_id) for pic_id in pic_id_list)

    if subFolder:
        fullPath = path_clear(subFolder, root_name)
    else:
        fullPath = root_name

    No = 0
    for res in res_yield:
        with open("{}_{}.jpg".format(fullPath, No), "wb") as file:
            file.write(res.content)
            file.flush()
        file.close()
        No += 1
