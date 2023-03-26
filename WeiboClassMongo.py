# -*- coding: utf-8 -*-
# @Time    : 2023/2/3 16:44
# @Author  : Euclid-Jie
# @File    : WeiboClassMongo.py
import random
import time

import pandas as pd
import pymongo
from tqdm import tqdm
from WeiboClass import WeiboClass
import os


class WeiboClassMongo(WeiboClass):
    # MongoDB Setting
    def MongoClient(self, DBName, collectionName):
        # 连接数据库
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        mydb = myclient[DBName]  # 数据库名称
        mycol = mydb[collectionName]  # 集合（表）
        return mycol

    def get_data(self):
        col = self.MongoClient('Weibo', self.key)
        for page in tqdm(range(1, self.total_pages + 1)):
            # 设置页数
            self.page = page
            # time.sleep(random.randint(1, 3))
            # 获取soup对象
            self.get_soup()
            list = self.soup.find_all('div', attrs={'class': 'card-wrap', 'action-type': 'feed_list_item'})
            for item in list:
                # 设置item，每个item实际上为一条微博
                self.item = item
                # 获取item中的元素
                self.get_data_df()
                # 写入
                col.insert_one(self.data_json)
        print('关键词【{}】数据已写入{}条数据'.format(self.key, len(list)))

    def main_get(self):
        """
        主函数，遍历关键词，每个关键词写入单独的文件
        :return:
        """

        for key in self.keyList:
            # 参数设置
            ## 设置关键词
            self.key = key
            ## 重置时间跨度
            self.timeEnd = self.timeEnd_0
            ## 设置存储路径
            self.FilePath = key + '.csv'

            print('-*' * 18)
            print('开始处理关键词【{}】的数据'.format(key))
            print('时间跨度为【{}】-【{}】'.format(self.timeBegin, self.timeEnd))

            ## 获取总页数
            self.get_total_pages()
            # 处理微博每次只能返回50条数据的问题
            if self.total_pages < self.limit:
                # 开始遍历每一页
                self.get_data()

            elif self.total_pages >= self.limit:
                while self.total_pages >= self.limit:
                    # 开始遍历每一页
                    self.get_data()
                    time.sleep(random.randint(1, 3))
                    # 更新时间跨度参数
                    timeEnd = self.timeEnd  # 记录更新前的时间跨度
                    self.update_time_span()
                    if self.timeBegin >= self.timeEnd:
                        print(f'参数更新超界，已停止{timeEnd}')
                        break
                    if self.timeEnd == timeEnd:  # 时间跨度参数更新无效,强制跳过该小时
                        print(f'参数更新无效，强制跳过{timeEnd}')
                        self.timeEnd = (pd.to_datetime(self.timeEnd) - pd.DateOffset(hours=1)).strftime('%Y-%m-%d-%H')
                    ## 获取总页数
                    self.get_total_pages()
                # 补充获取最后一个跨度的数据
                self.get_data()
