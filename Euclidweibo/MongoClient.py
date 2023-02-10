# -*- coding: utf-8 -*-
# @Time    : 2023/2/9 23:26
# @Author  : Euclid-Jie
# @File    : MongoClient.py
import pymongo


def MongoClient(DBName, collectionName):
    # 连接数据库
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient[DBName]  # 数据库名称
    mycol = mydb[collectionName]  # 集合（表）
    return mycol
