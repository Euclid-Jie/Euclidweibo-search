![Euclidweibo-search](https://socialify.git.ci/Euclid-Jie/Euclidweibo-search/image?language=1&name=1&owner=1&stargazers=1&theme=Light)
# 微博爬虫-指定关键词
[![wakatime](https://wakatime.com/badge/user/b638b33f-0c9e-4408-b427-258fe0b24ad0/project/018cf0d2-72e3-40dc-a5da-6d05ba35512c.svg)](https://wakatime.com/badge/user/b638b33f-0c9e-4408-b427-258fe0b24ad0/project/018cf0d2-72e3-40dc-a5da-6d05ba35512c)

爬取指定时间区间内，包含指定关键词、话题的原创微博，此代码长期维护，如有疑问欢迎`Issues`
## 快速开始

### 1、下载项目并安装依赖

- 直接使用`git clone`，或者直接点击蓝色的`<>Code` -> `Download ZIP`下载到本地进行解压也可

  ```bash
  https://github.com/Euclid-Jie/Euclidweibo-search.git
  ```

- 使用`pip`安装依赖

  ```bash
  pip install -r requirements.txt
  ```

### 2、设置Cookie

将`Cookie`写入`Cookie.txt`中，详见[注意事项](##注意事项)，80%的报错/运行异常由Cookie设置不正确引起，特录制获取Cookie的[视频](https://www.bilibili.com/video/BV1Sh4y1J7Yz)，欢迎观看，获取正确的Cookie

### 3、修改参数并运行`WeiboClassRun`

🛎️ **Attention!!** 目前有两种数据写入方式，请结合自身情选择选择，具体选择方式为修改`mongo_save`参数

- `mongo_save=False`：将输出写为`csv`文件，数据文件将以`csv`格式存储至`.Weibo\`目录下
- `mongo_save=True`：以默认`27017`端口连接`MongoDB`数据库，写入的`collection`名为`Weibo`

```python
# 设置参数
search_options = WeiboSearchOptions(
    # cookie文件路径
    cookie_path="cookie.txt",
    
    # 最小时间跨度更新页面数阈值，建议3~5
    limit=3,
    
    # 关键词
    keyword_list=["北师大", "北京师范大学", "北京师范大学统计学院", "BNU", "北师", "北京师范大学珠海校区"],
    
    # 开始时间, 格式为"YYYY-MM-DD-H"
    start_time="2020-01-01-0",
    
    # 结束时间, 格式为"YYYY-MM-DD-H"
    end_time="2020-01-10-0",
    
    # 是否要求微博内容严格包含关键词
    keyword_contain=True,
    
    # 设置为True，将数据写入MongoDB, 否则写入CSV
    mongo_save=True,
    
    # 默认为None, 每个关键词的数据将各存为一个文件
    # 如果进行设置，所有关键词将写入同一个csv，csv名为ColName，
    ColName="test",
)
```

## 更新日志

*20240312* 重构代码，解决相对应用问题

- New Feature: 可使用`selenium`自动更新`cookie`，详见`Euclidweibo\weibo_cookie.py`，当然保留了手动更新方式；
- Enhance: 自动获取`user`的总微博数，自动确定翻页次数

*20231215* 简化代码结构，废弃冗余代码

- 入口函数改为`WeiboClassRun.py`，调用`WeiboClassV1`
- 使用`search_options`方式进行参数设定

- `WeiboClassV2`, `WeiboClassV3`暂停止维护, 如有使用问题请提`issue`

*long long ago*

- 老版本`WeiboClassRun.py`已废弃，正式更新`WeiboClassV1.py`

- 另有批次请求版本`WeiboClassV2.py`，及多线程请求版本`WeiboClassV3.py`可供选择

- 若请求速度过快已封号推荐使用`V1`，或者传入`IP`代理

## 代码结构

```python
WeiboClassRun.py # 入口函数
WeiboClassV1.py # 主请求函数

EuclidWeibo.py # 工具包
Euclid_weibo_Test.py # 使用样例
WeiboClassV2.py # 主请求函数，在此更改参数，暂停止维护
WeiboClassV3.py # 主请求函数，多线程版本，在此更改参数，暂停止维护
```


## 输出文件字段说明

| 名称              | 含义                   |
| ----------------- | ---------------------- |
| keyWords          | 检索的关键词           |
| mid               | 微博标识ID，为一串数字 |
| time              | 微博发布时间           |
| nick_name         | 微博发布者昵称         |
| content           | 微博内容               |
| 转发数(reposts)   | 微博转发数             |
| 评价数(comments)  | 微博评价数             |
| 点赞数(attitudes) | 微博点赞数             |

## Euclidweibo package

🛎️开发已完成，可直接使用`pip`安装，具体见可[`EuclidSearchPackage`](https://github.com/Euclid-Jie/EuclidSearchPackage)

```markdown
Euclidweibo
    - __init--.py  # init
    - Get_item_url_list.py  # 获取指定关键词下的微博列表[未完成]
    - Get_longTextContent.py  # 轮子函数，获取完整微博内容
    - Get_single_weibo_data.py  # 获取单个微博内容信息
    - Get_single_weibo_details.py  # 获取单个微博的评论、转发、点赞信息[未完成]
    - Get_user_all_weibo.py  # 获取某个用户的所有微博信息，或部分(可指定筛选条件)
    - Get_user_info.py  # 获取微博用户账号信息
Euclid_weibo_Test.py  # 功能展示, 所展示的均为可用
```

## 注意事项

- `header`中的`cookie`需要登录微博网页版后获取，登录网址为：https://s.weibo.com/
- `cookie`一定之间后会过期，建议每次使用前更新`cookie`
- 由于微博存在显示限制，只会显示时间跨度内最接近现在的30页，或50页，且最低时间跨度单位为小时，故如果某个小时内的数据超过了显示限制，只能获取该小时内的30页、或50页
