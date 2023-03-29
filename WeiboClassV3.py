# -*- coding: utf-8 -*-
# @Time    : 2023/3/29 10:25
# @Author  : Euclid-Jie
# @File    : WeiboClassV3.py
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from WeiboClassV2 import WeiboClassV2
from Euclidweibo import *


class WeiboClassV3(WeiboClassV2):
    def __init__(self, keyWord=None, method=None, baseUrl=None, Mongo=True, max_work_count=20, LongText=False):
        super().__init__(keyWord, method, baseUrl, Mongo)
        self.LongText = LongText
        self.max_work_count = max_work_count

    @staticmethod
    def run_thread_pool_sub(target, args, max_work_count):
        with ThreadPoolExecutor(max_workers=max_work_count) as t:
            res = [t.submit(target, i) for i in args]
            return res

    def main(self, beginTime, endTime, ColName=None):
        if ColName is None:
            ColName = self.keyWord
        if self.Mongo:
            _COL = MongoClient('Weibo', ColName)
        else:
            _COL = CsvClient('Weibo', ColName)

        print(">>> get blog info begin ...")
        NewEndTime = endTime
        while NewEndTime > beginTime:
            print("\t " + "-*" * 20)
            print("\t time span: {} - {}".format(beginTime, NewEndTime))
            print("\t " + "-*" * 20)
            self.get_url_list(beginTime, NewEndTime)
            if len(self.UrlList) <= 5:
                break
            print("\n\t >>> get blog data begin ...")
            # multitask get data
            allData = []
            results = self.run_thread_pool_sub(Get_single_weibo_data_async,
                                               [mblogid.split("/")[-1] for mblogid in self.UrlList],
                                               max_work_count=self.max_work_count)
            for future in as_completed(results):
                data_json = future.result()
                allData.append(data_json)

            # LongText process
            if self.LongText:
                print("\t >>> get LongText begin ...")
                allData_long = []
                results = self.run_thread_pool_sub(Get_longTextContent,
                                                   allData,
                                                   max_work_count=self.max_work_count)
                for future in as_completed(results):
                    data_json = future.result()
                    allData_long.append(data_json)
                allData = allData_long

            # write data and update span
            BreakOrNot = True
            tmpTime = NewEndTime
            print("\t >>> write blog data begin ...")
            for data_json in allData:
                if not self.LongText:
                    data_json['longTextContent'] = ''
                try:
                    selectedData = self.select_field(data_json)
                    _COL.insert_one(selectedData)
                    tmpTime = pd.to_datetime(selectedData['time']).strftime("%Y-%m-%d-%H")
                except json.decoder.JSONDecodeError:
                    pass
                except KeyError:
                    pass
                # upDate date
                if NewEndTime > tmpTime:
                    NewEndTime = tmpTime
                    BreakOrNot = False
            print("\t >>> write blog data done")
            if BreakOrNot:
                break

        print(">>> get blog info done")


if __name__ == '__main__':
    WeiboClassV3('量化实习', Mongo=False).main('2023-02-11-00', '2023-03-27-21')
