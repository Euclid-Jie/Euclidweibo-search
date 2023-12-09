"""
# -*- coding: utf-8 -*-
# @Time    : 2023/12/9 11:00
# @Author  : Euclid-Jie
# @File    : weiboTime.py
"""
import pandas as pd


class weiboTime:
    """
    用于处理微博时间的类, 直接返回为str格式, 例如: 2021-01-01-0
    """

    def __init__(self, time_dt: [pd.Timestamp, str]):
        if isinstance(time_dt, str):
            self.time_dt = pd.to_datetime(time_dt, format="%Y-%m-%d-%H")
        elif isinstance(time_dt, pd.Timestamp):
            self.time_dt = time_dt
        else:
            raise TypeError("time_dt must be pd.Timestamp or str")

    @property
    def dt(self):
        return self.time_dt

    @property
    def str(self):
        return self.time_dt.strftime("%Y-%m-%d-%H")

    @property
    def dt_hour(self):
        """
        忽略分钟和秒, 只保留小时, 例如: Timestamp('2021-01-01 10:00:00')
        """
        return pd.to_datetime(self.str, format="%Y-%m-%d-%H")

    def __str__(self):
        return self.time_dt.strftime("%Y-%m-%d-%H")

    def lag_hour(self, lag):
        """
        用于将时间向前或向后移动lag小时
        :param lag: int
        :return: weiboTime
        """
        return weiboTime(self.time_dt + pd.tseries.offsets.Hour(lag))
