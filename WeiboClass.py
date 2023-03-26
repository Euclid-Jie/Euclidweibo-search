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
import datetime
from tqdm import tqdm


class WeiboClass(object):
    """
    用于查找指定时间跨度的，关键词对应的微博内容
    输出微博正文内容，微博发布人昵称，发布时间，转评赞数据
    """

    def __init__(self, keyList, timeBegin, timeEnd, limit, contains):
        """
        传入参数
        :param keyList: 关键词列表，目前为
        :param timeBegin: 开始时间，格式为 '2022-09-01-0'
        :param timeEnd: 结束时间，格式为 '2022-09-30-0'
        :param limit: 设置时间跨度更新的，敏感值，一般设置3-5
        :param contains: 是否必须精确包含关键词
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
        self.limit = limit  # 用于控制更新时间跨度，默认为20
        self.contains = contains

    def set_header(self):
        """
        设置header内容，可根据自己的更改cookie
        :return:
        """
        with open('cookie.txt', 'rt', encoding='utf-8') as f:
            cookie = f.read().strip()
        self.header = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/104.0.0.0 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
                      '*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'Cookie': cookie
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

        # self.URL = 'https://s.weibo.com/weibo?q=' + self.key + '&typeall=1&suball=1&timescope=custom:' + self.timeBegin + ':' + self.timeEnd + '&Refer=g&page=' + str(
        #     self.page)

        response = requests.get(self.URL, headers=self.header, timeout=60)  # 使用request获取网页
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
        time = self.item.find('div', 'from').a.text.replace(' ', '').replace('\n', '')
        if '今天' not in time:
            self.time = time

        nick_name = self.item.find('p', attrs={'node-type': "feed_list_content"}).attrs['nick-name']
        try:  # 部分微博内容需要展开，直接取feed_list_content_full
            content_raw = self.item.find('p', attrs={'node-type': "feed_list_content_full"}) \
                .text.replace(' ', '').replace('\n', '')
        except:
            content_raw = self.item.find('p', attrs={'node-type': "feed_list_content"}) \
                .text.replace(' ', '').replace('\n', '')
        content = remove_upprintable_chars(content_raw)
        ## 处理转评赞
        act = get_number(self.item.find('div', 'card-act').find_all('li'))

        # 其他数据

        # 拼接数据
        self.data_json = {
            'mid': mid,
            'time': time,
            'nick_name': nick_name,
            'content': content,
            '转发数': act[0],
            '评价数': act[1],
            '点赞数': act[2]
        }

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
        #  TODO 有可能一个小时内数据量极大，超过50页，时间跨度更新无效，需要考虑
        mytime = self.time  # 2021年11月09日14:54(非今年)、10月30日19:31(今年）
        if '年' in mytime:  # 如果非当前年的数据，会额外显示年的信息
            mytime = pd.to_datetime(mytime.replace('年', '-').replace('月', '-').replace('日', '-'))
            mytime_lag = (mytime - pd.DateOffset(hours=1)).strftime('%Y-%m-%d-%H')  # '2021-11-09-15'
            self.timeEnd = mytime_lag
        # TODO 如果是今天
        elif '今天' in mytime:
            mytime


        else:
            mytime = pd.to_datetime(
                str(datetime.date.today().year) + '-' + mytime.replace('月', '-').replace('日', '-'))
            mytime_lag = (mytime - pd.DateOffset(hours=1)).strftime('%Y-%m-%d-%H')  # '2021-11-09-15'
            self.timeEnd = mytime_lag

        print('时间跨度已更新为【{}】-【{}】'.format(self.timeBegin, self.timeEnd))

    def get_data(self):
        ## 存储该关键词的所有数据
        out_df = pd.DataFrame()
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
                # 拼接每条数据
                out_df = pd.concat([out_df, pd.DataFrame(self.data_json, index=[0])])

        print('关键词【{}】数据已写入{}条数据'.format(self.key, len(out_df)))
        self.save_data(out_df, self.FileFullPath, self.FilePath)

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
            self.FileFullPath = os.path.join(os.getcwd(), self.FilePath)

            print('-*' * 18)
            print('开始处理关键词【{}】的数据'.format(key))
            print('时间跨度为【{}】-【{}】'.format(self.timeBegin, self.timeEnd))
            print('文件将存储在：{}'.format(self.FileFullPath))

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

            # 删除重复及content中含有单独关键字的情况
            out_df = pd.read_csv(self.FilePath)
            out_df.drop_duplicates(keep='first', inplace=True)
            if self.contains:
                out_df = out_df[out_df.content.str.contains(key)]
            else:
                pass
            print('关键词【{}】数据已去重完毕，共写入{}条数据'.format(self.key, len(out_df)))
            out_df.to_csv(self.FilePath, header=True, index=False, encoding='utf_8_sig')
