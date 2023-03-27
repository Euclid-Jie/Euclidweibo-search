# -*- coding: utf-8 -*-
# @Time    : 2023/3/26 19:42
# @Author  : Euclid-Jie
# @File    : WeiboClassV2.py
from urllib.parse import urlencode
from Euclidweibo import *


class WeiboClassV2:
    def __init__(self, keyWord=None, method=None, baseUrl=None, Mongo=True):
        self.keyWord = keyWord
        self.UrlList = None
        self.baseUrl = 'https://s.weibo.com/weibo?'
        self.method = method
        self.Mongo = Mongo

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

    def get_url_list(self, beginTime: str, endTime: str):
        page = 0
        NetPage = True
        self.UrlList = []
        print("\n\t >>> get blog url begin ...")
        while NetPage:
            page += 1
            targetUrl = self.UrlFormat(self.keyWord, beginTime, endTime, page)
            onePageList = Get_item_url_list(targetUrl)
            tmpLen = len(self.UrlList)
            self.UrlList.extend(onePageList)
            self.UrlList = list(set(self.UrlList))
            if len(self.UrlList) == tmpLen:
                NetPage = False
            print('\r\t\t page: {}, len: {}'.format(page, len(self.UrlList)), end='')
        print("\n\t >>> get blog url done")

    @staticmethod
    def select_field(data):
        selectedData = {
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
        return selectedData

    def main(self, beginTime, endTime, ColName):
        if self.Mongo:
            _COL = MongoClient('Weibo', ColName)
        else:
            _COL = CsvClient('Weibo', ColName)

        print(">>> get blog info begin ...")
        NewEndTime = endTime
        while NewEndTime > beginTime:
            print('\t time span: {} - {}'.format(beginTime, NewEndTime), end='')
            self.get_url_list(beginTime, NewEndTime)
            if len(self.UrlList) <= 5:
                break
            print("\t >>> write blog url begin ...")
            for mblogid in tqdm(self.UrlList):
                data_json = Get_single_weibo_data(mblogid.split("/")[-1])
                selectedData = self.select_field(data_json)
                _COL.insert_one(selectedData)
                # upDate date
                tmpTime = pd.to_datetime(selectedData['time']).strftime("%Y-%m-%d-%H")
                if NewEndTime >= tmpTime:
                    NewEndTime = tmpTime
            print("\t >>> write blog url done")
        print(">>> get blog info done")


if __name__ == '__main__':
    self = WeiboClassV2('复试', Mongo=False)
    self.main('2023-03-10-00', '2023-03-11-00', '复试')
