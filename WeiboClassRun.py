# -*- coding: utf-8 -*-
# time: 2022/10/1 11:32
# file: WeiboClassRun.py
# author: Euclid_Jie
from WeiboClass import WeiboClass

# 设置参数
# keyList = ['北师大', '北京师范大学', '北京师范大学统计学院', 'BNU', '北师', '北京师范大学珠海校区']
# keyList = ['#北京师范大学120周年校庆#']
keyList = ['北师大']
timeBegin = '2021-12-25-0'
timeEnd = '2022-01-05-0'
# 运行函数
WeiboClass(keyList, timeBegin, timeEnd, 3).main_get()
