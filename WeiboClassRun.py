# -*- coding: utf-8 -*-
# time: 2022/10/1 11:32
# file: WeiboClassRun.py
# author: Euclid_Jie
import pymongo
from datetime import datetime
from WeiboClassV1 import WeiboClassV1
import pandas as pd


def MongoClient(DBName, collectionName):
    # 连接数据库
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient[DBName]  # 数据库名称
    mycol = mydb[collectionName]  # 集合（表）
    return mycol


def read_mongo(DBName, collectionName, query=None, no_id=True):
    """
    Read from Mongo and Store into DataFrame
    :param DBName: mongoDB dataBase's name
    :param collectionName: mongoDB dataBase's collection's name
    :param query: a selection for data
    :param no_id: do not write _id column to data
    :return: pd.DataFrame
    """
    # Connect to MongoDB
    if query is None:
        query = {}
    col = MongoClient(DBName, collectionName)
    # Make a query to the specific DB and Collection
    cursor = col.find(query)
    # Expand the cursor and construct the DataFrame
    df = pd.DataFrame(list(cursor))
    # Delete the _id
    if no_id and '_id' in df:
        del df['_id']
    return df.drop_duplicates()


# 设置参数
keyList = ['北师大', '北京师范大学', '北京师范大学统计学院', 'BNU', '北师', '北京师范大学珠海校区']
timeBegin = '2023-05-01-0'
timeEnd = '2023-06-01-0'

if __name__ == '__main__':
    # 运行函数[两种写入方法二选一]
    # 1、使用csv写入
    WeiboClassV1(limit=3, contains=True, Mongo=False).main_get(keyList, timeBegin, timeEnd)
    # 2、使用用MongoDB数据库
    # WeiboClassV1(limit=3, contains=True, Mongo=True).main_get(keyList, timeBegin, timeEnd)

    # ---------------读取MongoDB数据至CSV
    # for key in keyList:
    #     df = read_mongo('Weibo', key, query=None, no_id=True)
    #     df = df.loc[df['time'].apply(lambda x: isinstance(x, datetime))]
    #     # df = df[df['time'].str.contains('02月')].copy()
    #     df = df.loc[df['time'] >= pd.to_datetime("2023-05-01")]
    #     df.to_csv(r'outData\2023-05-{}.csv'.format(key), index=False, encoding='utf-8-sig')
