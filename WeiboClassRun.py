# -*- coding: utf-8 -*-
# time: 2022/10/1 11:32
# file: WeiboClassRun.py
# author: Euclid_Jie
from WeiboClass import WeiboClass
# 设置参数
keyList = ['北师大']
#keyList = ['#北京师范大学120周年校庆#']
timeBegin = '2022-10-01-0'
timeEnd = '2022-10-20-0'
# 运行函数
WeiboClass(keyList, timeBegin, timeEnd, 3).main_get()
