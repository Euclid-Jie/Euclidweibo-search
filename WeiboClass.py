# -*- coding: utf-8 -*-
# time: 2022/10/1 11:24
# file: WeiboClass.py
# author: Euclid_Jie
import os
import time
import random
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

from tqdm import tqdm


class WeiboClass(object):
    """
    用于查找指定时间跨度的，关键词对应的微博内容
    输出微博正文内容，微博发布人昵称，发布时间，转评赞数据
    """

    def __init__(self, keyList, timeBegin, timeEnd):
        """
        传入参数
        :param keyList: 关键词列表，目前为
        :param timeBegin: 开始时间，格式为 '2022-09-01-0'
        :param timeEnd: 结束时间，格式为 '2022-09-30-0'
        """
        self.URL = None
        self.key = None
        self.soup = None
        self.page = 1  # 初始化设定
        self.data_df = None
        self.item = None
        self.header = None
        self.keyList = keyList
        self.timeEnd_0 = timeEnd
        self.timeEnd = timeEnd
        self.timeBegin = timeBegin

    def set_header(self):
        """
        设置header内容，可根据自己的更改cookie
        :return:
        """
        self.header = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/104.0.0.0 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
                      '*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'cookie': 'SINAGLOBAL=9170657301486.473.1664549732363; '
                      'SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WW18ADvK4GwUUQp3dLa50Un5JpX5KMhUgL'
                      '.FoME1h24SoMceo52dJLoI7D8UgSjIgxkCJLL; ALF=1696123950; SSOLoginState=1664587954; '
                      'SCF=AjAZ8VlJRKXsr4vWqu_1y14puHW6Tnn8liIxNVc_7C9Sas5TSljEY5hJV0AV_SXXWr9iUaehlMp90pKYfysRb0w.; '
                      'SUB=_2A25OM-jiDeRhGeFM41MY9inKyTyIHXVtSV0qrDV8PUNbmtAfLXjkkW9NQLjCKQoLIHRcBsZsa3L4lqneqWOmZCA_'
                      '; _s_tentry=login.sina.com.cn; UOR=,,login.sina.com.cn; '
                      'Apache=3576157376630.0825.1664587956644; '
                      'ULV=1664587956677:7:2:7:3576157376630.0825.1664587956644:1664554051073 '
        }

    def get_soup(self):
        """
        根据URL返回soup对象
        :return:
        """

        # 设置header
        self.set_header()
        self.URL = 'https://s.weibo.com/weibo?q=' + self.key + '&scope=ori&suball=1&timescope=custom:' + self.timeBegin + ':' + self.timeEnd + '&page=' + str(
            self.page)
        response = requests.get(self.URL, headers=self.header)  # 使用request获取网页
        html = response.content.decode('utf-8', 'ignore')  # 将网页源码转换格式为html
        self.soup = BeautifulSoup(html, 'lxml')

    def get_data_df(self):
        """
        根据每条微博内容，返回各元素
        :return: DataFrame格式
        """

        # 几个轮子函数
        ## 移出部分不可见字符
        def remove_upprintable_chars(s):
            """移除所有不可见字符"""
            return ''.join(x for x in s if x.isprintable())

        ## 处理转评赞数据
        def get_number(act):
            """
            处理转评赞数据，返回[1,0,1]表示转发1次，评论0条，赞1个
            :param act:
            :return:
            """
            # 转发
            z = re.findall(r"\d+", act[0].text)
            # 评论
            p = re.findall(r"\d+", act[1].text)
            # 点赞
            d = re.findall(r"\d+", act[2].text)
            out = []
            for item in [z, p, d]:
                try:
                    number = int(item[0])
                    out.append(number)
                except:
                    out.append(0)
            return out

        # self.item为list中的一个,list即为当前页面的微博条数列表，一个item为一条微博
        ## 获取对应元素
        mid = self.item.attrs['mid']
        # 记录time对象，用于更新时间跨度
        self.time = self.item.find('div', 'from').a.text.replace(' ', '').replace('\n', '')
        nick_name = self.item.find('p', attrs={'node-type': "feed_list_content"}).attrs['nick-name']
        content_raw = self.item.find('p', attrs={'node-type': "feed_list_content"}).text.replace(' ', '').replace('\n',
                                                                                                                  '')
        content = remove_upprintable_chars(content_raw)
        ## 处理转评赞
        act = get_number(self.item.find('div', 'card-act').find_all('li'))

        # 拼接数据
        self.data_df = pd.DataFrame({
            'mid': [mid],
            'time': [self.time],
            'nick_name': [nick_name],
            'content': [content],
            '转发数': [act[0]],
            '评价数': [act[1]],
            '点赞数': [act[2]]
        })

    def get_total_pages(self):
        """
        获取当前关键词下共有多少页
        :return: int
        """
        self.get_soup()
        try:
            self.total_pages = len(
                self.soup.find('ul', attrs={'class': 's-scroll', 'node-type': "feed_list_page_morelist"}).find_all(
                    'li'))
        except:
            self.total_pages = 1

    def save_data(self, data_df, FileFullPath, FilePath):
        """
        轮子函数，用于存储数据，可实现对已存在文件的追加写入
        :param data_df: 目标数据
        :param FileFullPath: 全路径，包括文件名和后缀
        :param FilePath: 文件名，包括后缀
        :return:
        """
        if os.path.isfile(FileFullPath):
            data_df.to_csv(FilePath, mode='a', header=False, index=False, encoding='utf_8_sig')
        else:
            data_df.to_csv(FilePath, mode='w', header=True, index=False, encoding='utf_8_sig')

    def update_time_span(self):
        """
        用于更新self.timeEnd及self.timeBegin
        :return:
        """

        # 轮子函数，用于转换日期
        def to_time_str(year, timelist):
            month = timelist[0]
            if len(month) == 1:
                month = '0' + month
            day = timelist[1]
            if len(day) == 1:
                day = '0' + day
            hour = int(timelist[2])
            if hour != 24:
                hour += 1
            else:
                # TODO 如果是24则要换天
                pass
            hour = str(hour)
            output = year + '-' + month + '-' + day + '-' + hour
            return output

        mytime = self.time
        timelist = [mytime.split(':')[0].split('月')[0], mytime.split(':')[0].split('月')[1].split('日')[0],
                    mytime.split(':')[0].split('月')[1].split('日')[1]]
        self.timeEnd = to_time_str('2022', timelist)
        print('时间跨度已更新为【{}】-【{}】'.format(self.timeBegin, self.timeEnd))

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
            FilePath = key + '.csv'
            FileFullPath = os.path.join(os.getcwd(), FilePath)

            print('-*' * 18)
            print('开始处理关键词【{}】的数据'.format(key))
            print('时间跨度为【{}】-【{}】'.format(self.timeBegin, self.timeEnd))
            print('文件将存储在：{}'.format(FileFullPath))

            ## 获取总页数
            self.get_total_pages()
            # 处理微博每次只能返回50条数据的问题
            if self.total_pages < 50:
                # 开始遍历每一页

                ## 存储该关键词的所有数据
                out_df = pd.DataFrame()
                for page in tqdm(range(1, self.total_pages + 1)):
                    # 设置页数
                    self.page = page
                    time.sleep(random.randint(1, 3))
                    # 获取soup对象
                    self.get_soup()
                    list = self.soup.find_all('div', attrs={'class': 'card-wrap', 'action-type': 'feed_list_item'})
                    for item in list:
                        # 设置item，每个item实际上为一条微博
                        self.item = item
                        # 获取item中的元素
                        self.get_data_df()
                        # 拼接每条数据
                        out_df = pd.concat([out_df, self.data_df])

                print('关键词【{}】数据已写入{}条数据'.format(self.key, len(out_df)))
                self.save_data(out_df, FileFullPath, FilePath)

            elif self.total_pages >= 49:
                while self.total_pages >= 49:
                    # 开始遍历每一页

                    ## 存储该关键词的所有数据
                    out_df = pd.DataFrame()
                    for page in tqdm(range(1, self.total_pages + 1)):
                        # 设置页数
                        self.page = page
                        time.sleep(random.randint(1, 3))
                        # 获取soup对象
                        self.get_soup()
                        list = self.soup.find_all('div', attrs={'class': 'card-wrap', 'action-type': 'feed_list_item'})
                        for item in list:
                            # 设置item，每个item实际上为一条微博
                            self.item = item
                            # 获取item中的元素
                            self.get_data_df()
                            # 拼接每条数据
                            out_df = pd.concat([out_df, self.data_df])
                    print('关键词【{}】数据已写入{}条数据'.format(self.key, len(out_df)))
                    self.save_data(out_df, FileFullPath, FilePath)

                    # 更新时间跨度参数
                    time.sleep(random.randint(5, 10))
                    self.update_time_span()
                    ## 获取总页数
                    self.get_total_pages()

                ## 存储该关键词的所有数据
                out_df = pd.DataFrame()
                for page in tqdm(range(1, self.total_pages + 1)):
                    # 设置页数
                    self.page = page
                    time.sleep(random.randint(1, 3))
                    # 获取soup对象
                    self.get_soup()
                    list = self.soup.find_all('div', attrs={'class': 'card-wrap', 'action-type': 'feed_list_item'})
                    for item in list:
                        # 设置item，每个item实际上为一条微博
                        self.item = item
                        # 获取item中的元素
                        self.get_data_df()
                        # 拼接每条数据
                        out_df = pd.concat([out_df, self.data_df])

                print('关键词【{}】数据已写入{}条数据'.format(self.key, len(out_df)))
                self.save_data(out_df, FileFullPath, FilePath)

            # 删除重复
            out_df = pd.read_csv(FilePath)
            out_df.drop_duplicates(keep='first', inplace=True)
            print('关键词【{}】数据已去重完毕，共写入{}条数据'.format(self.key, len(out_df)))
            out_df.to_csv(FilePath, header=True, index=False, encoding='utf_8_sig')
