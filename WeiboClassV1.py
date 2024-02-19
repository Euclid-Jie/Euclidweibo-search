# -*- coding: utf-8 -*-
# @Time    : 2023/4/16 11:16
# @Author  : Euclid-Jie
# @File    : WeiboClassV1.py
import datetime
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, NamedTuple, Optional
import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm
from pydantic import BaseModel

from Euclidweibo import (
    Set_header,
    Get_soup_data,
    remove_upPrintable_chars,
    MongoClient,
    CsvClient,
    weiboTime,
)


class searchSpan(NamedTuple):
    start: weiboTime
    end: weiboTime


class WeiboSearchOptions(BaseModel):
    # class options
    cookie_path: str = "cookie.txt"
    limit: int = 5  # 用于控制更新时间跨度，默认为5

    # target data options
    keyword_list: List = ["人工智能"]
    start_time: str = "2023-03-01-0"
    end_time: str = "2023-08-01-0"
    keyword_contain: bool = False

    # save options
    mongo_save: bool = False
    ColName: Optional[str] = (
        None  # if u want to save all keywords in one collection, set this
    )


class WeiboClassV1:
    def __init__(self, options: WeiboSearchOptions):
        self._options = options

        # setting header
        self.header = Set_header(self._options.cookie_path)

        # other object
        # 这些变量会在获取数据过程中被赋值
        self._COL = None
        self.keyWord = None
        self.URL = None
        self.key = None
        self.soup = None
        self.data_df = None
        self.item = None
        self.beginTime = None
        self.endTime = None
        self.total_pages = None

    def get_single_page_soup(self, search_span: searchSpan, page: int = 1):
        # get Url like : https://s.weibo.com/weibo?q=%E5%8C%97%E5%B8%88%E5%A4%A7&typeall=1&suball=1&timescope=custom:2023-04-02-0:2023-04-03-0
        URL = f"https://s.weibo.com/weibo?q={self.keyWord}&scope=ori&suball=1&timescope=custom:{search_span.start}:{search_span.end}&page={page}"
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

    def get_single_weibo_json(self, blog: BeautifulSoup) -> dict:
        # blog is a single bolg data, type is Bs4.soup
        mid = blog.attrs["mid"]
        mblogid = re.findall(
            r"(?<=/)[A-Za-z0-9]+(?=\?)", blog.find("div", "from").a["href"]
        )[0]
        uid = re.findall(r"(?<=/)\d+(?=\?)", blog.find("div", "avator").a["href"])[0]
        nick_name = blog.find("p", attrs={"node-type": "feed_list_content"}).attrs[
            "nick-name"
        ]

        time_str = blog.find("div", "from").a.text.replace(" ", "").replace("\n", "")
        time_dt = self.format_time(time_str)

        # 部分微博内容需要展开，直接取feed_list_content_full
        content = blog.find("p", attrs={"node-type": "feed_list_content_full"})
        if content:
            content_raw = content.text.replace(" ", "").replace("\n", "")
        else:

            content_raw = (
                blog.find("p", attrs={"node-type": "feed_list_content"})
                .text.replace(" ", "")
                .replace("\n", "")
            )
        content = remove_upPrintable_chars(content_raw)

        ## 处理转评赞
        act = self.get_act_number(blog.find("div", "card-act").find_all("li"))
        data_json = {
            "keyWords": self.keyWord,
            "mid": mid,
            "mblogid": mblogid,
            "uid": uid,
            "nick_name": nick_name,
            "time": time_dt,
            "content": content,
            "转发数": act[0],
            "评价数": act[1],
            "点赞数": act[2],
        }

        # 返回内容需严格包含关键词
        if self._options.keyword_contain:
            if self.keyWord in data_json["content"]:
                return data_json
            else:
                return None
        else:
            return data_json

    def get_total_pages(self, search_span: searchSpan) -> int:
        """
        获取当前关键词下共有多少页
        :return: int
        """
        self.get_single_page_soup(search_span=search_span, page=1)
        try:
            self.total_pages = len(
                self.soup.find(
                    "ul",
                    attrs={"class": "s-scroll", "node-type": "feed_list_page_morelist"},
                ).find_all("li")
            )
        except AttributeError:
            self.total_pages = 1

    @staticmethod
    def format_time(time_str) -> pd.Timestamp:
        """
        格式化时间, 返回pd.Timestamp格式
        """
        if "年" in time_str:  # 非今年的数据, 会显示具体的年月日
            time_str = time_str.replace("年", "-").replace("月", "-").replace("日", "-")
        elif "今天" in time_str:  # 今天的数据, 只显示时分, 需要增加年月日
            time_str = datetime.date.today().strftime("%Y-%m-%d") + time_str.replace(
                "今天", "-"
            )
        elif "分钟前" in time_str:  # 距离数据采集时间一小时内, 使用当前时间回望
            minutes_num = re.findall(r"\d+", time_str)[0]
            time_str = datetime.datetime.now() - datetime.timedelta(
                minutes=int(minutes_num)
            )  # 实际上为dt格式, 不是str, 不过不影响pd.to_datetime()
        else:  # 今年非今天的数据, 需要增加年
            time_str = (
                datetime.date.today().strftime("%Y")
                + "-"
                + time_str.replace("月", "-").replace("日", "-")
            )
        time_dt = pd.to_datetime(time_str)
        return time_dt

    def get_all_pages_data(self, search_span: searchSpan) -> weiboTime:
        """
        获取当前关键词下所有页的数据, 并写入数据库;
        返回的是最早的一条数据的时间, 用于更新时间跨度
        """
        min_time_dt = search_span.end.dt
        with tqdm(range(1, self.total_pages + 1)) as t:
            for page in t:
                # time.sleep(random.randint(1, 3))
                self.get_single_page_soup(search_span=search_span, page=page)
                bolg_list = self.soup.find_all(
                    "div", attrs={"class": "card-wrap", "action-type": "feed_list_item"}
                )
                successful_num = 0
                # 开启并行获取data_json
                res = self.run_thread_pool_sub(
                    self.get_single_weibo_json, bolg_list, max_work_count=24
                )
                for future in as_completed(res):
                    data_json = future.result()
                    if data_json:
                        self._COL.insert_one(data_json)
                        successful_num += 1
                        # min time update
                        if data_json["time"] <= min_time_dt:
                            min_time_dt = data_json["time"]
                t.set_postfix({"状态": "已写num:{}".format(successful_num)})
        return weiboTime(min_time_dt)

    @staticmethod
    def update_time_span(old_time_span: searchSpan, new_end: weiboTime) -> searchSpan:
        """
        更新时间跨度, 如果不更新, 返回None
        需要说明的是, 由于微博的时间跨度是按照小时来的, 所以更新时间跨度时, 需要将new_end增加一小时
        但是如果增加一小时后, 跨度超过了old_time_span的end, 则不更新
        """
        if old_time_span.start.dt < new_end.dt < old_time_span.end.dt:
            if new_end.lag_hour(1).dt_hour < old_time_span.end.dt_hour:
                return searchSpan(start=old_time_span.start, end=new_end.lag_hour(1))
        else:
            return None

    def main_get(self):
        print("-*" * 20)
        for self.keyWord in self._options.keyword_list:
            # set each keyWord's collection name
            itemColName = (
                self._options.ColName if self._options.ColName else self.keyWord
            )
            self._COL = (
                MongoClient("Weibo", itemColName)
                if self._options.mongo_save
                else CsvClient("Weibo", itemColName)
            )

            print("> get {} blog data begin ... ".format(self.keyWord))
            # get time span
            search_span = searchSpan(
                start=weiboTime(self._options.start_time),
                end=weiboTime(self._options.end_time),
            )
            while search_span is not None:
                # update time span
                print(
                    ">> time span: {} - {}".format(search_span.start, search_span.end)
                )
                self.get_total_pages(search_span)
                if self.total_pages <= self._options.limit:
                    break
                # get all pages data
                new_end_time: weiboTime = self.get_all_pages_data(search_span)

                # update time end
                search_span = self.update_time_span(search_span, new_end_time)
            print("> get all blog info done")
