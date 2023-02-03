# -*- coding: utf-8 -*-
# @Time    : 2023/2/3 16:44
# @Author  : Euclid-Jie
# @File    : WeiboClassMongo.py
import pymongo
from tqdm import tqdm
from WeiboClass import WeiboClass


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
