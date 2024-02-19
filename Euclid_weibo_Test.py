# -*- coding: utf-8 -*-
# @Time    : 2023/2/9 13:01
# @Author  : Euclid-Jie
# @File    : Euclid_weibo_Test.py
from Euclidweibo import *

# # 1、 get single weibo's reposts data, the data will write to MongoDB
# Get_single_weibo_details('reposts', mblogid='MrOtA75Fd', header=Set_header('cookie.txt')).main_get()
#
# # 2、 get single weibo's data
# data_json = Get_single_weibo_data(mblogid='MrOtA75Fd', header=Set_header('cookie.txt'))
# print(data_json)

# 3、 set the url(contains keyword), then get the weibo url list, item in list is "1562868034/MkXTBh9Fk", which is contains uid and mblogid
# url_list = Get_item_url_list('https://s.weibo.com/weibo?q=杭州公园', proxies=False)
# print(url_list)

# # 4、get user's info
# data_json = Get_user_info('1202150843')
# print(data_json)

# 5、get user's all blog
# Get_user_all_weibo(7416119836, 100, begin=50)

# 6、get user's all blog and pic
Get_user_all_weibo(6572153436, csv=True, pic=True)
