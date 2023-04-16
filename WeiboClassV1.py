# -*- coding: utf-8 -*-
# @Time    : 2023/4/16 11:16
# @Author  : Euclid-Jie
# @File    : WeiboClassV1.py
import datetime
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm

from Euclidweibo import Set_header, Get_soup_data, remove_upPrintable_chars, MongoClient, CsvClient


class WeiboClassV1(object):
    def __init__(self, contains=True, limit=5, Mongo=True):
        """
        :param limit: 设置时间跨度更新的，敏感值，一般设置3-5
        :param contains: 是否必须精确包含关键词
        :param Mongo: 默认写入MongoDB, False时, 写入EXCEL
        """
        # para  init

        self._COL = None
        self.Mongo = Mongo
        self.limit = limit  # 用于控制更新时间跨度，默认为5
        self.contains = contains
        self.header = Set_header('cookie.txt')

        # other object
        self.keyWord = None
        self.URL = None
        self.key = None
        self.soup = None
        self.data_df = None
        self.item = None
        self.beginTime = None
        self.endTime = None
        self.total_pages = None

    def get_single_page_soup(self, page=1):
        # get Url like : https://s.weibo.com/weibo?q=%E5%8C%97%E5%B8%88%E5%A4%A7&typeall=1&suball=1&timescope=custom:2023-04-02-0:2023-04-03-0
        URL = 'https://s.weibo.com/weibo?q=' + self.keyWord + '&scope=ori&suball=1&timescope=custom:' + \
              self.beginTime + ':' + self.endTime + '&page=' + str(page)
        self.soup = Get_soup_data(URL, self.header)

    @staticmethod
    def get_act_number(act):
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
            except IndexError:
                out.append(0)
        return out

    @staticmethod
    def run_thread_pool_sub(target, args, max_work_count):
        with ThreadPoolExecutor(max_workers=max_work_count) as t:
            res = [t.submit(target, i) for i in args]
            return res

    def get_single_weibo_json(self, blog: BeautifulSoup):
        # blog is a single bolg data, type is Bs4.soup
        mid = blog.attrs['mid']
        uid = re.findall('(?<=/)\d+(?=\?)', blog.find('div', 'avator').a['href'])[0]
        nick_name = blog.find('p', attrs={'node-type': "feed_list_content"}).attrs['nick-name']

        time_str = blog.find('div', 'from').a.text.replace(' ', '').replace('\n', '')
        time_dt = self.format_time(time_str)

        # 部分微博内容需要展开，直接取feed_list_content_full
        content = blog.find('p', attrs={'node-type': "feed_list_content_full"})
        if content:
            content_raw = content.text.replace(' ', '').replace('\n', '')
        else:

            content_raw = blog.find('p', attrs={'node-type': "feed_list_content"}).text.replace(' ', '').replace('\n', '')
        content = remove_upPrintable_chars(content_raw)

        ## 处理转评赞
        act = self.get_act_number(blog.find('div', 'card-act').find_all('li'))
        data_json = {
            'mid': mid,
            'uid': uid,
            'nick_name': nick_name,
            'time': time_dt,
            'content': content,
            '转发数': act[0],
            '评价数': act[1],
            '点赞数': act[2]
        }

        # 返回内容需严格包含关键词
        if self.contains:
            if self.keyWord in data_json['content']:
                return data_json
            else:
                return None

    def get_total_pages(self):
        """
        获取当前关键词下共有多少页
        :return: int
        """
        self.get_single_page_soup()
        try:
            self.total_pages = len(self.soup.find('ul', attrs={'class': 's-scroll', 'node-type': "feed_list_page_morelist"}).find_all('li'))
        except AttributeError:
            self.total_pages = 1

    @staticmethod
    def format_time(time_str):
        if '年' in time_str:  # 非今年的数据, 会显示具体的年月日
            time_str = time_str.replace('年', '-').replace('月', '-').replace('日', '-')
        elif '今天' in time_str:  # 今天的数据, 只显示时分, 需要增加年月日
            time_str = datetime.date.today().strftime("%Y-%m-%d") + time_str.replace('今天', '-')
        elif '分钟前' in time_str:  # 距离数据采集时间一小时内, 使用当前时间回望
            minutes_num = re.findall('/d+', time_str)[0]
            time_str = datetime.datetime.now() - datetime.timedelta(minutes=minutes_num)  # 实际上为dt格式, 不是str, 不过不影响pd.to_datetime()
        else:  # 今年非今天的数据, 需要增加年
            time_str = datetime.date.today().strftime('%Y') + '-' + time_str.replace('月', '-').replace('日', '-')
        time_dt = pd.to_datetime(time_str)
        return time_dt

    def get_all_pages_data(self):
        min_time_dt = pd.to_datetime(self.endTime, format='%Y-%m-%d-%H')
        with tqdm(range(1, self.total_pages + 1)) as t:
            for page in t:
                # time.sleep(random.randint(1, 3))
                self.get_single_page_soup(page)
                bolg_list = self.soup.find_all('div', attrs={'class': 'card-wrap', 'action-type': 'feed_list_item'})
                successful_num = 0
                # 开启并行获取data_json
                res = self.run_thread_pool_sub(self.get_single_weibo_json, bolg_list, max_work_count=24)
                for future in as_completed(res):
                    data_json = future.result()
                    if data_json:
                        self._COL.insert_one(data_json)
                        successful_num += 1
                        # min time update
                        if data_json['time'] <= min_time_dt:
                            min_time_dt = data_json['time']
                t.set_postfix({"状态": "已写num:{}".format(successful_num)})
        return min_time_dt

    def main_get(self, keyList, beginTime, endTime, ColName=None):
        self.beginTime = beginTime
        self.endTime = endTime

        print('-*' * 20)
        for self.keyWord in keyList:
            if ColName is None:
                ColName = self.keyWord
            if self.Mongo:
                self._COL = MongoClient('Weibo', ColName)
            else:
                self._COL = CsvClient('Weibo', ColName)

            print('> get {} blog data begin ... '.format(self.keyWord))
            NewEndTime = endTime
            while NewEndTime > beginTime:
                # update time span
                self.endTime = NewEndTime
                print('>> time span: {} - {}'.format(self.beginTime, self.endTime))
                self.get_total_pages()
                if self.total_pages <= self.limit:
                    break
                # get all pages data
                min_time_dt = self.get_all_pages_data()

                # update time end
                if pd.to_datetime(NewEndTime, format='%Y-%m-%d-%H') >= min_time_dt:
                    min_time_dt_lag = min_time_dt + pd.tseries.offsets.Hour(1)
                    NewEndTime = min_time_dt_lag.strftime('%Y-%m-%d-%H')
                else:
                    break
            print("> get all blog info done")


if __name__ == '__main__':
    timeBegin = '2023-03-01-0'
    timeEnd = '2023-03-10-0'
    demoClass = WeiboClassV1(Mongo=False)
    demoClass.main_get(['北师大', '珠海'], timeBegin, timeEnd)
