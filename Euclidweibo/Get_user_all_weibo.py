# -*- coding: utf-8 -*-
# @Time    : 2023/3/21 21:32
# @Author  : Euclid-Jie
# @File    : Get_user_all_weibo.py
import json
import requests
from tqdm import tqdm
import os
from Euclidweibo import *
from Euclidweibo.Utils import Get_json_data


def Get_user_all_weibo(uid, totalPages, begin=1, query=None, colName=None, csv=False):
    """
    the code is to get one's all or part blogs
    :param uid: the user's id
    :param totalPages: the total pages u want get, almost 20 blogs of each page
    :param begin: the beginning page u want to start
    :colName: the collection name u want to store
    """
    if not colName:
        colName = uid
    if not csv:
        _COL = MongoClient('Weibo', 'uid_{}'.format(colName))
    else:
        _COL = CsvClient('Weibo', 'uid_{}'.format(colName))
    current_dir = os.path.abspath(os.path.dirname(__file__))
    parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
    _HEADER = Set_header(os.path.join(parent_dir, 'cookie.txt'))
    with tqdm(range(begin, totalPages)) as t:
        for pages in t:
            if query:
                URL = 'https://weibo.com/ajax/profile/searchblog?uid={}&page={}&feature=0&q={}'.format(uid, pages, query)
            else:
                URL = 'https://weibo.com/ajax/statuses/mymblog?uid={}&page={}'.format(uid, pages)
            data_json = Get_json_data(URL, _HEADER)
            for single_weibo in data_json['data']['list']:
                if '展开' in single_weibo['text']:
                    longText_URL = 'https://weibo.com/ajax/statuses/longtext?id={}'.format(single_weibo['mblogid'])
                    response = requests.get(longText_URL, headers=_HEADER, timeout=60)  # 使用request获取网页
                    html = response.content.decode('utf-8', 'ignore')  # 将网页源码转换格式为html
                    longTextContent = json.loads(html)['data']['longTextContent']
                    single_weibo['longTextContent'] = longTextContent
                else:
                    single_weibo['longTextContent'] = ''

                part_data = {
                    'time': single_weibo['created_at'],
                    'mid': single_weibo['mid'],
                    'nick_name': single_weibo['user']['screen_name'],
                    'attitudes_count': single_weibo['attitudes_count'],
                    'comments_count': single_weibo['comments_count'],
                    'reposts_count': single_weibo['reposts_count'],
                    'text': single_weibo['text'],
                    'text_raw': single_weibo['text_raw'],
                    'longTextContent': single_weibo['longTextContent'],
                    # 'online_users_number': single_weibo['page_info']['media_info']['online_users_number']
                }
                _COL.insert_one(part_data)
            t.set_postfix({"状态": "已写入{}条".format(len(data_json['data']['list']))})


if __name__ == '__main__':
    Get_user_all_weibo(2656274875, 100, query='主播说联播', colName='主播说联播', csv=True)
