# -*- coding: utf-8 -*-
# @Time    : 2023/3/26 19:42
# @Author  : Euclid-Jie
# @File    : WeiboClassV2.py
import time
from urllib.parse import urlencode
from Euclidweibo import *


class WeiboClassV2:
    def __init__(self, keyWord=None, method=None, baseUrl=None, Mongo=True, proxies=False):
        self.keyWord = keyWord
        self.UrlList = None
        self.baseUrl = 'https://s.weibo.com/weibo?'
        self.method = method
        self.Mongo = Mongo
        self.proxies = proxies

    def UrlFormat(self, keyWords, timeBegin: str, timeEnd: str, page: int):
        """
        :param keyWords: 关键词
        :param timeBegin: 开始时间
        :param timeEnd: 结束时间
        :param page: 页数
        :return: targetUrl

        """
        query = {'q': keyWords,
                 'typeall': 1,
                 'suball': 1,
                 'timescope': 'custom:{}:{}'.format(timeBegin, timeEnd),
                 'Refer': 'g',
                 'page': page
                 }
        targetUrl = self.baseUrl + urlencode(query)
        return targetUrl

    def get_url_list(self, beginTime: str, endTime: str, proxies):
        page = 0
        NetPage = True
        self.UrlList = []
        print("\n\t >>> get blog url begin ...")
        while NetPage:
            page += 1
            targetUrl = self.UrlFormat(self.keyWord, beginTime, endTime, page)
            onePageList = Get_item_url_list(targetUrl, proxies)
            tmpLen = len(self.UrlList)
            self.UrlList.extend(onePageList)
            self.UrlList = list(set(self.UrlList))
            if len(self.UrlList) == tmpLen:
                NetPage = False
            print('\r\t\t page: {}, len: {}'.format(page, len(self.UrlList)), end='')

    @staticmethod
    def select_field(data):
        if 'page_info' in data.keys():
            video_url = data['page_info']['media_info']['mp4_720p_mp4']
        else:
            video_url = ''

        selectedData = {
            # base filed
            'time': data['created_at'],
            'mid': data['mid'],
            'nick_name': data['user']['screen_name'],
            'useId': data['user']['id'],
            'mblogUrl': "https://weibo.com/{}/{}".format(data['user']['id'], data['mid']),
            # addition field
            'attitudes_count': data['attitudes_count'],
            'comments_count': data['comments_count'],
            'reposts_count': data['reposts_count'],
            'text': data['text'],
            'text_raw': data['text_raw'],
            'longTextContent': data['longTextContent'],
            'video_url': video_url
        }
        return selectedData

    def main(self, beginTime, endTime, ColName=None):
        if ColName is None:
            ColName = self.keyWord
        if self.Mongo:
            _COL = MongoClient('Weibo', ColName)
        else:
            _COL = CsvClient('Weibo', ColName)

        print(">> get blog info begin ...")
        NewEndTime = endTime
        while NewEndTime > beginTime:
            print('\t time span: {} - {}'.format(beginTime, NewEndTime), end='')
            self.get_url_list(beginTime, NewEndTime, self.proxies)
            if len(self.UrlList) <= 5:
                break
            print("\t >>> write blog url begin ...")
            BreakOrNot = True
            for mblogid in tqdm(self.UrlList):
                try:
                    data_json = Get_single_weibo_data(mblogid.split("/")[-1], proxies=self.proxies)
                    if data_json:
                        data_json = Get_longTextContent(data_json)
                        selectedData = self.select_field(data_json)
                        _COL.insert_one(selectedData)
                    else:
                        pass
                except json.decoder.JSONDecodeError:
                    pass
                except KeyError:
                    pass
                # upDate date
                tmpTime = pd.to_datetime(selectedData['time']).strftime("%Y-%m-%d-%H")
                if NewEndTime >= tmpTime:
                    NewEndTime = tmpTime
                    BreakOrNot = False
            if BreakOrNot:
                break
            print("\t >>> write blog url done")
        print(">>> get blog info done")


if __name__ == '__main__':
    a = time.time()
    WeiboClassV2('央视频', Mongo=False).main('2023-03-11-00', '2023-03-27-21')
    print(time.time() - a)
