# -*- coding: utf-8 -*-
# @Time    : 2023/3/21 21:32
# @Author  : Euclid-Jie
# @File    : Get_user_all_weibo.py
# @desc    : 仅能被调用, 不能直接被执行
from typing import Optional
import warnings
from .Get_Pic import Get_Pic
from .Utils import *


def deal_single_weibo(para):
    (single_weibo, _COL, _HEADER, uid, pic) = para
    if "展开" in single_weibo["text"]:
        longText_URL = "https://weibo.com/ajax/statuses/longtext?id={}".format(
            single_weibo["mblogid"]
        )
        response = requests.get(
            longText_URL, headers=_HEADER, timeout=60
        )  # 使用request获取网页
        html = response.content.decode("utf-8", "ignore")  # 将网页源码转换格式为html
        try:
            longTextContent = json.loads(html)["data"]["longTextContent"]
            single_weibo["longTextContent"] = longTextContent
        except KeyError:
            # 说明正文中有展开, 而不是真的需要展开
            single_weibo["longTextContent"] = ""
    else:
        single_weibo["longTextContent"] = ""

    # del time
    date_string = single_weibo["created_at"]
    date_object = datetime.strptime(date_string, "%a %b %d %H:%M:%S %z %Y")
    formatted_date = date_object.strftime("%Y-%m-%d %H:%M:%S")

    part_data = {
        "time": formatted_date,
        "mid": single_weibo["mid"],
        "nick_name": single_weibo["user"]["screen_name"],
        "attitudes_count": single_weibo["attitudes_count"],
        "comments_count": single_weibo["comments_count"],
        "reposts_count": single_weibo["reposts_count"],
        "text": single_weibo["text"],
        "text_raw": single_weibo["text_raw"],
        "longTextContent": single_weibo["longTextContent"],
        # 'online_users_number': single_weibo['page_info']['media_info']['online_users_number']
    }
    _COL.insert_one(part_data)
    if pic:
        if single_weibo["pic_num"] > 0:
            if "pic_ids" in single_weibo.keys():
                pic_id_list = list(single_weibo["pic_ids"])
            elif "pic_infos" in single_weibo.keys():
                pic_id_list = list(single_weibo["pic_infos"].keys())
            else:
                pic_id_list = None
            if pic_id_list:
                root_name = int(
                    datetime.strptime(
                        single_weibo["created_at"], "%a %b %d %H:%M:%S +0800 %Y"
                    ).timestamp()
                )
                Get_Pic(
                    pic_id_list=pic_id_list,
                    root_name=str(root_name),
                    subFolder="weibo/{}_pic".format(uid),
                )

    return 1


def Get_user_all_weibo(
    uid: int,
    totalPages: Optional[int] = None,
    begin: Optional[int] = 1,
    query: Optional[str] = None,
    colName: Optional[str] = None,
    csv: Optional[bool] = False,
    pic: Optional[bool] = False,
):
    """
    the code is to get one's all or part blogs
    :param uid: the user's id
    :param totalPages: the total pages u want get, almost 20 blogs of each page
    :param begin: the beginning page u want to start
    :param query:
    :param colName: the collection name u want to store
    :param csv:
    :param pic:
    """
    if not totalPages:
        totalPages = 100
        warnings.warn("totalPages is not specified, the default value is 100")
    if not colName:
        colName = uid
    if not csv:
        _COL = MongoClient("Weibo", "uid_{}".format(colName))
    else:
        _COL = CsvClient("Weibo", "uid_{}".format(colName))
    current_dir = os.path.abspath(os.path.dirname(__file__))
    parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
    _HEADER = Set_header(os.path.join(parent_dir, "cookie.txt"))
    with tqdm(range(begin, totalPages)) as t:
        for pages in t:
            if query:
                URL = "https://weibo.com/ajax/profile/searchblog?uid={}&page={}&feature=0&q={}".format(
                    uid, pages, query
                )
            else:
                URL = "https://weibo.com/ajax/statuses/mymblog?uid={}&page={}".format(
                    uid, pages
                )
            data_json = Get_json_data(URL, _HEADER)
            param_list = [
                (single_weibo, _COL, _HEADER, uid, pic)
                for single_weibo in data_json["data"]["list"]
            ]
            res = run_thread_pool_sub(deal_single_weibo, param_list, max_work_count=24)
            for future in as_completed(res):
                res = future.result()
                pass
            t.set_postfix({"状态": "已写入{}条".format(len(data_json["data"]["list"]))})
