![Euclidweibo-search](https://socialify.git.ci/Euclid-Jie/Euclidweibo-search/image?language=1&name=1&owner=1&stargazers=1&theme=Light)
# 微博爬虫-指定关键词
爬取指定时间区间内，包含指定关键词、话题的原创微博，此代码长期维护，如有疑问欢迎`Issues`

## 代码结构

```python
WeiboClass.py # 主类
WeiboClassMongo.py # 继承类，写入数据到MongoDB数据库
WeiboClassRun.py # 调用类，在其中修改参数并运行
```

## 输入参数

- 将Cookie写入Cookie.txt中，详见[注意事项](##注意事项)。

- 关键词列表，元素为`str`格式

  ```python
  keyList = ['北京师范大学','120周年校庆']
  keyList = ['%23北京师范大学120周年校庆%23'] # %23转义后即为#，表示爬取包含话题的微博
  ```

- 时间区间，各位为`YY-mm-dd-hh`

  ```python
  timeBegin = '2022-09-01-0' # 开始时间
  timeEnd = '2022-09-08-10' # 结束时间
  ```

- 其他参数

  ```python
  limit # 设置时间跨度更新的，敏感值，一般设置3-5
  contains # 所获取的微博内容是否严格包含关键词，若为True则要求严格包含
  ```

  严格包含的意思举例说明，若关键词为“西南财大”时，可检索包含“西南”+“财大”，即两词分开，若设置为True则仅返回两次连续的内容，即“西南财大”

## 调用方式

设置`header`及参数后，直接运行`WeiboClassRun.py`，即可开始爬取工作

## 输出内容

| 名称      | 含义                   |
| --------- | ---------------------- |
| mid       | 微博标识ID，为一串数字 |
| time      | 微博发布时间           |
| nick_name | 微博发布者昵称         |
| content   | 微博内容               |
| 转发数    | 微博转发数             |
| 评价数    | 微博评价数             |
| 点赞数    | 微博点赞数             |

## 注意事项

- `header`中的`cookie`需要登录微博网页版后获取，登录网址为：https://s.weibo.com/
- `cookie`一定之间后会过期，建议每次使用前更新`cookie`
- 由于微博存在显示限制，只会显示时间跨度内最接近现在的30页，或50页，且最低时间跨度单位为小时，故如果某个小时内的数据超过了显示限制，只能获取该小时内的30页、或50页