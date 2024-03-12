# 前提是配置并在指定端口的Chorme浏览器中登录微博, 然后不要关闭浏览器, 运行此脚本既可自动获取并更新cookie
# 如何配置指定端口的Chorme, 见以下教程
# https://euclid-jie.gitbook.io/gitbookdemo/pa-chong-xiang-guan/selenium-pa-chong-xiang-guan#id-5-tuo-guan-zhi-ding-duan-kou-de-liu-lan-qi
from selenium import webdriver
import requests
from bs4 import BeautifulSoup
from .Set_header import Set_header
from pathlib import Path

__all__ = ["weiboCookie"]


class weiboCookie:
    def __init__(self, port=9222, cookie_path="cookie.txt"):
        self.port = port
        self.cookie_path = cookie_path
        if not Path(self.cookie_path).exists():
            raise FileNotFoundError(f"{self.cookie_path} not found")

    def update_cookie(self):
        if self.test_cookie():
            return
        else:
            self.options = webdriver.ChromeOptions()
            self.options.add_experimental_option(
                "debuggerAddress", f"127.0.0.1:{self.port}"
            )  # 接管
            self.driver = webdriver.Chrome(options=self.options)  # 设置参数
            self.driver.get("https://s.weibo.com/?Refer=北师大")  # 跳转网页
            cookies = self.driver.get_cookies()  # 获取cookie
            cookies_str = "; ".join(
                [f'{cookie["name"]}={cookie["value"]}' for cookie in cookies]
            )
            with open(self.cookie_path, "w") as f:
                f.write(cookies_str)
                
            if self.test_cookie():
                print("cookie已更新")
            else:
                print("cookie更新失败, 请查看是否登录微博")

    def test_cookie(self) -> bool:
        response = requests.get("http://weibo.cn", cookies=Set_header(self.cookie_path))
        if response.status_code == 200:
            html = response.text
            soup = BeautifulSoup(html, features="xml")
            title = soup.title.string
            if title == "我的首页":
                print("有效cookie")
                return True
            else:
                # Cookie已失效
                print("失效cookie")
                return False
