# -*- coding: utf-8 -*-
# @Time    : 2023/2/9 22:21
# @Author  : Euclid-Jie
# @File    : Get_single_weibo_details.py
from tqdm import tqdm
from .Get_single_weibo_data import Get_single_weibo_data
from .MongoClient import MongoClient
from .EuclidDataTools import CsvClient
from .Utils import Get_json_data
from .Get_longTextContent import Get_longTextContent

__all__ = ["Get_single_weibo_details"]


class Get_single_weibo_details:
    """
    Usually a single weibo have three import information:
        1: reposts
        https://weibo.com/ajax/statuses/repostTimeline?id=4866288901690071&page=1&moduleID=feed&count=10
        2: comments
        https://weibo.com/ajax/statuses/buildComments?is_reload=1&id=4866288901690071&is_show_bulletin=2
        3: attitudes
        https://weibo.com/ajax/statuses/likeShow?id=4866288901690071&attitude_type=0&attitude_enable=1&page=1&count=10

    Choose one or the other by setting para "method"
        method = ['reposts', 'comments', 'attitudes']
    """

    def __init__(self, method, mblogid, header, ColName=None, Mongo=True):
        """
        :param method: ['reposts', 'comments', 'attitudes'],
        :param mblogid: just like "MrOtA75Fd",
        :param header: Set_header()
        :return: None
        """
        self.page = None
        self.item = None
        self.pages = None
        self.mid = None
        self.total_pages = None
        self.singe_weibo_data = None
        self.mblogid = mblogid
        self.method = method
        self.header = header
        self.ColName = ColName
        self.Mongo = Mongo
        self.singe_weibo_data = Get_single_weibo_data(self.mblogid)
        self.Get_single_weibo_infos()

        if self.ColName is None:
            self.ColName = self.mblogid + "_" + self.method

        if self.Mongo:
            self._COL = MongoClient("Weibo", self.ColName)
        else:
            self._COL = CsvClient("Weibo", self.ColName)

    def Get_single_weibo_infos(self):
        self.total_pages = {
            "reposts_count": self.singe_weibo_data["reposts_count"],
            "comments_count": self.singe_weibo_data["comments_count"],
            "attitudes_count": self.singe_weibo_data["attitudes_count"],
        }

        self.mid = self.singe_weibo_data["mid"]

    def get_data_json(self):
        data_json = {
            "mblogid": self.item["mblogid"],
            "mid": self.item["id"],
            "time": self.item["created_at"],
            "uid": self.item["user"]["id"],
            "nick_name": self.item["user"]["screen_name"],
            "isLongText": self.item["isLongText"],
            "attitudes_count": self.item["attitudes_count"],
            "comments_count": self.item["comments_count"],
            "reposts_count": self.item["reposts_count"],
            "text": self.item["text"],
            "text_raw": self.item["text_raw"],
        }
        return Get_longTextContent(data_json)

    def get_comments_data_json(self, son=False):
        if son:
            like_counts = self.item["like_count"]
        else:
            like_counts = self.item["like_counts"]
        data_json = {
            "mblogid": self.mblogid,
            "mid": self.item["id"],
            "root_mid": self.item["rootid"],
            "time": self.item["created_at"],
            "uid": self.item["user"]["id"],
            "nick_name": self.item["user"]["screen_name"],
            "comments_type": self.item["readtimetype"],
            "like_counts": like_counts,
            "text": self.item["text"],
            "text_raw": self.item["text_raw"],
        }
        return data_json

    def get_attitude_data_json(self):
        user_data_json = self.item["user"]
        data_json = {
            "mblogid": self.mblogid,
            "uid": user_data_json["id"],
            "time": user_data_json["created_at"],
            "nick_name": user_data_json["screen_name"],
        }
        return data_json

    def rolling_get_son_comments(self):
        # TODO 进一步处理grandson comments 需要发起新请求
        # https://weibo.com/ajax/statuses/buildComments?flow=0&is_reload=1&id=4891070384571362&is_show_bulletin=2&is_mix=1&fetch_level=1&max_id=0&count=20&uid=1618051664
        comments_count = 0

        # deal root comments
        data_json = self.get_comments_data_json()
        # write to mongoDB
        self._COL.insert_one(data_json)
        comments_count += 1

        # deal son comments
        if "comments" in self.item.keys():
            if self.item["comments"].__len__() > 0:
                for sonItem in self.item["comments"]:
                    self.item = sonItem
                    data_json = self.get_comments_data_json(True)
                    self._COL.insert_one(data_json)
                    comments_count += 1

        return comments_count

    def Get_reposts_info(self):
        total_pages = int(self.total_pages["comments_count"] / 15)
        # total_pages = 100
        with tqdm(range(0, total_pages + 1)) as t:
            for self.page in t:
                t.set_description("pages:{}".format(self.page))  # bar's left info
                URL = "https://weibo.com/ajax/statuses/repostTimeline?id={}&page={}&moduleID=feed&count=10".format(
                    self.mid, self.pages
                )
                data_json = Get_json_data(URL, self.header)
                reposts_list = data_json["data"]
                for self.item in reposts_list:
                    data_json = self.get_data_json()
                    # write to mongoDB
                    self._COL.insert_one(data_json)
                t.set_postfix(
                    {"状态": "已成功写入{}条".format(len(reposts_list))}
                )  # bar's right info

        return data_json

    def Get_comments_info(self):
        # 类知乎评论, 滚动更新
        total_comments_num = 0
        # 默认按热度另有按时间
        # https://weibo.com/ajax/statuses/buildComments?flow=1&is_reload=1&id=4902567073546360&is_show_bulletin=2&is_mix=0&count=10&uid=2989616011&fetch_level=0
        URL = "https://weibo.com/ajax/statuses/buildComments?flow=1&is_reload=1&id={}&is_show_bulletin=2&is_mix=0&count=10&fetch_level=0".format(
            self.mid
        )
        # init
        data_json = Get_json_data(URL, self.header)
        total_comments = data_json["total_number"]

        with tqdm(
            total=total_comments, desc="{} comments get".format(self.mid)
        ) as pbar:
            while True:
                max_id = data_json["max_id"]
                # comments data
                comments_list = data_json["data"]
                for self.item in comments_list:
                    comments_count = self.rolling_get_son_comments()
                    total_comments_num += comments_count
                    pbar.update(1)
                    pbar.set_postfix(
                        {"状态": "已成功写入{}条".format(comments_count)}
                    )  # bar's right info
                if max_id == 0:
                    break
                else:
                    URL = "https://weibo.com/ajax/statuses/buildComments?flow=1&is_reload=1&id={}&is_show_bulletin=2&is_mix=0&max_id={}&count=20&fetch_level=0".format(
                        self.mid, max_id
                    )
                    data_json = Get_json_data(URL, self.header)
        print("共写入{}条".format(total_comments_num))

    def Get_attitudes_info(self):
        total_pages = int(self.total_pages["attitudes_count"] / 20)
        with tqdm(range(0, total_pages + 2)) as t:
            for self.page in t:
                t.set_description("pages:{}".format(self.page))  # bar's left info
                URL = "https://weibo.com/ajax/statuses/likeShow?id={}&attitude_type=0&attitude_enable=1&page={}&count=20".format(
                    self.mid, self.pages
                )
                data_json = Get_json_data(URL, self.header)
                reposts_list = data_json["data"]
                for self.item in reposts_list:
                    data_json = self.get_attitude_data_json()
                    # write to mongoDB
                    self._COL.insert_one(data_json)
                t.set_postfix(
                    {"状态": "已成功写入{}条".format(len(reposts_list))}
                )  # bar's right info

    def main_get(self):
        if self.method == "reposts":
            self.Get_reposts_info()
        elif self.method == "comments":
            self.Get_comments_info()
        elif self.method == "attitudes":
            self.Get_attitudes_info()
        else:
            raise AttributeError(
                "please set correct para method: reposts, comments or attitudes"
            )
