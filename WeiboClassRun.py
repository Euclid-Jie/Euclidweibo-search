# -*- coding: utf-8 -*-
# time: 2022/10/1 11:32
# file: WeiboClassRun.py
# author: Euclid_Jie
from WeiboClass import WeiboClass

# keyList = ['北京师范大学', '北京师范大学统计学院', '北师', '北师大', '北师大珠海校区', 'bnu']
# keyList = ['北京师范大学统计学院', '北师', '北师大', '北师大珠海校区', 'bnu']
keyList = ['北师大','北师']
timeBegin = '2022-09-01-0'
timeEnd = '2022-10-01-0'

WeiboClass(keyList, timeBegin, timeEnd).main_get()
