# -*- coding: utf-8 -*-
# @Time    : 2023/2/9 20:01
# @Author  : Euclid-Jie
# @File    : Get_user_info.py
import json
import requests
from Euclidweibo import Set_header


def Get_user_info(uid, header):
    """
    base weibo user's uid, get his gender

    future can get user's more detail info

    base url : https://weibo.com/ajax/profile/info?uid=1202150843
    """

    URL = 'https://weibo.com/ajax/profile/info?uid={}'.format(uid)

    response = requests.get(URL, headers=header, timeout=60)  # 使用request获取网页
    html = response.content.decode('utf-8', 'ignore')  # 将网页源码转换格式为html
    data_json = json.loads(html)['data']

    return data_json


if __name__ == '__main__':
    data = Get_user_info('7416119836', Set_header('../cookie.txt'))
    # followers_count
    print(data['user']['followers_count'])
    # gender
    print(data['user']['gender'])
