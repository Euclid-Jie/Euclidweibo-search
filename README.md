![Euclidweibo-search](https://socialify.git.ci/Euclid-Jie/Euclidweibo-search/image?language=1&name=1&owner=1&stargazers=1&theme=Light)
# 微博爬虫-指定关键词
爬取指定时间区间内，包含指定关键词、话题的原创微博，此代码长期维护，如有疑问欢迎`Issues`

老版本`WeiboClassRun.py`已废弃，正式更新`WeiboClassV2.py`，另有多线程版本`WeiboClassV3.py`可供选择

🛎️ **Attention!!** 目前有两种数据写入方式，请结合自身情选择选择，具体选择方式为修改`WeiboClassV2.py`中的`Mongo`参数，默认为`True`

- `Mongo=False`：将输出写为csv文件
- `Mongo=True`：MongoDB数据库

## 代码结构

```python
EuclidWeibo # 工具包
WeiboClassV2.py # 主函数，在此更改参数
WeiboClassV3.py # 主函数，多线程版本，在此更改参数
```

## Euclidweibo package

🛎️开发已完成，可直接使用`pip`安装，具体见可[EuclidSearchPackage](https://github.com/Euclid-Jie/EuclidSearchPackage)

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

## 运行方式

### 1、设置Cookie

将Cookie写入Cookie.txt中，详见[注意事项](##注意事项)。

### 2、修改参数并运行

```python
WeiboClassV2('量化实习', Mongo=False).main('2023-03-11-00', '2023-03-27-21')
```

### 3、参数说明

- 关键词，`str`格式

  ```python
  keyWord = '北京师范大学'
  keyList = '%23北京师范大学120周年校庆%23' # %23转义后即为#，表示爬取包含话题的微博
  ```

- 时间区间，各位为`YY-mm-dd-hh`

  ```python
  timeBegin = '2022-09-01-00' # 开始时间
  timeEnd = '2022-09-08-10' # 结束时间
  ```

- 其他参数

  ```python
  Mongo=False  # 设置为写入csv 或 MongoDB
  ColName=None  # 存储的文件名
  max_work_count=20  # 线程池个数
  LongText=False  # 是否需要长文本, 开启将降速
  ```


## 输出内容

| 名称              | 含义                   |
| ----------------- | ---------------------- |
| mid               | 微博标识ID，为一串数字 |
| time              | 微博发布时间           |
| nick_name         | 微博发布者昵称         |
| Text              | 微博内容               |
| Text_raw          | 原始内容               |
| LongText_content  | 长内容格式             |
| 转发数(reposts)   | 微博转发数             |
| 评价数(comments)  | 微博评价数             |
| 点赞数(attitudes) | 微博点赞数             |

## 注意事项

- `header`中的`cookie`需要登录微博网页版后获取，登录网址为：https://s.weibo.com/
- `cookie`一定之间后会过期，建议每次使用前更新`cookie`
- 由于微博存在显示限制，只会显示时间跨度内最接近现在的30页，或50页，且最低时间跨度单位为小时，故如果某个小时内的数据超过了显示限制，只能获取该小时内的30页、或50页