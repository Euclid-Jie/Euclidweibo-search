# -*- coding: utf-8 -*-
# time: 2022/10/1 11:32
# file: WeiboClassRun.py
# author: Euclid_Jie
from WeiboClass import WeiboClass

# TODO 时间跨度更新会超出查询范围，需要解决
# 设置参数
keyList = ['北师']
# keyList = ['#北京师范大学120周年校庆#']
# keyList = ['美团民宿']
timeBegin = '2022-12-01-0'
timeEnd = '2022-12-02-23'
# 运行函数
WeiboClass(keyList, timeBegin, timeEnd, limit=3, contains=False).main_get()
