### 一、前言

July Novel是一个Flask Web后端项目，为JulyNovel-React提供GraphQL数据接口。
同时，通过在多台服务器部署此项目，实现分布式爬虫，抓取各大小说站点的书本
（仅供开发学习用途，并且只抓取免费公开书籍，遵循robots协议）

### 二、部署

在Cent OS上部署此项目。

[CentOS 部署July Novel 详细步骤](http://www.cnblogs.com/jiajin/p/8507083.html)

相关文件配置

1.vim /usr/local/nginx/conf/nginx.conf
配置nginx，开启https及http重定向到https
基于nginx-1.2.2
```
    server {
        listen     80;
        server_name www.yourdomain.com;
        return    301 https://$server_name$request_uri;
        location / {
            include     uwsgi_params;
            uwsgi_pass  localhost:5000;
            uwsgi_param UWSGI_PYHOME    /root/anaconda3/envs/web;
            uwsgi_param UWSGI_CHDIR     /home/web/JulyNovel;
            uwsgi_param UWSGI_SCRIPT    manage:app;
        }

        }

    server {
        listen     443 ssl;
        server_name  www.yourdomain.com;
        ssl_certificate 1_www.yourdomain.com_bundle.crt;
        ssl_certificate_key 2_www.yourdomain.com.key;
        ssl_session_timeout 5m;
        ssl_protocols TLSv1 TLSv1.1 TLSv1.2; #按照这个协议配置
        ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:HIGH:!aNULL:!MD5:!RC4:!DHE;#按照这个套件配置
        ssl_prefer_server_ciphers on;
        #charset koi8-r;
        access_log  /home/web/JulyNovel/logs/access.log;
        error_log /home/web/JulyNovel/logs/error.log;

        location / {
            include     uwsgi_params;
            uwsgi_pass  localhost:5000;
            uwsgi_param UWSGI_PYHOME    /root/anaconda3/envs/web;
            uwsgi_param UWSGI_CHDIR     /home/Web/JulyNovel;
            uwsgi_param UWSGI_SCRIPT    manage:app;

        }

        #error_page  404              /404.html;

        # redirect server error pages to the static page /50x.html
        #
        error_page   500 502 503 504  /50x.html;
        location = /50x.html {
            root   html;
        }

        # proxy the PHP scripts to Apache listening on 127.0.0.1:80
        #
        #location ~ \.php$ {
        #    proxy_pass   http://127.0.0.1;
        #}

        # pass the PHP scripts to FastCGI server listening on 127.0.0.1:9000
        #
        #location ~ \.php$ {
        #    root           html;
        #    fastcgi_pass   127.0.0.1:9000;
        #    fastcgi_index  index.php;
        #    fastcgi_param  SCRIPT_FILENAME  /scripts$fastcgi_script_name;
        #    include        fastcgi_params;
        #}

        # deny access to .htaccess files, if Apache's document root
        # concurs with nginx's one
        #
        #location ~ /\.ht {
        #    deny  all;
        #}
    }

```


2.vim /home/web/JulyNovel/config.py
配置MariaDB，Redis，Aliyun OSS
```python
# -*- coding: utf-8 -*-

class Config:
    REDIS_KEY = "your_redis_auth"
    REDIS_SERVER = "your_db_ip"

    MARIADB_SERVER = "mysql+mysqlconnector://db_account:db_password@db_ip/db_name"

    OSS_KEY_ID = "your oss key id"
    OSS_KEY_SECRET ="your oss key secret"
    END_POINT = "oss-cn-shanghai.aliyuncs.com"
    BUCKET_NAME = "yourbucketname"
    HOST = "https://yourbucketname.oss-cn-shanghai.aliyuncs.com/"
```

3.vim /home/web/manage_uwsgi.sh
配置uWSGI管理启动停止脚本
```linux
#!/bin/bash
if [ ! -n "$1" ]
then
    echo "Usages: sh uwsgiserver.sh [start|stop|restart]"
    exit 0
fi

if [ $1 = start ]
then
    psid=`ps aux | grep "uwsgi" | grep -v "grep" | wc -l`
    if [ $psid -gt 4 ]
    then
        echo "uwsgi is running!"
        exit 0
    else
        uwsgi /etc/uwsgi.ini
        echo "Start uwsgi service [OK]"
    fi


elif [ $1 = stop ];then
    killall -9 uwsgi
    echo "Stop uwsgi service [OK]"
elif [ $1 = restart ];then
    killall -9 uwsgi
    /usr/bin/uwsgi --ini /etc/uwsgi.ini
    echo "Restart uwsgi service [OK]"

else
    echo "Usages: sh uwsgiserver.sh [start|stop|restart]"
fi
```


### 三、GraphQL API 示例
#### Query
>查询小说排行榜，向下遍历子节点并展开；
>展开过程中动态加载简介summary、书类bookType；
>book对象上包裹Rank节点，描述book对象在不同排行榜下所处位置（sort）;
>可控制排行榜下的book数目
```js
query getRankList($rankTypeId: ID = 1, $totalCount: Int, $withBookTypeName: Boolean = false, $withSummary: Boolean = false) {
  rankType(rankTypeId: $rankTypeId) {
    typeId
    typeName
    rankList(totalCount: $totalCount) {
      rankTypeId
      book {
        bookId
        bookName
        cover
        banner
        summary @include(if: $withSummary)
        bookType @include(if: $withBookTypeName) {
          typeName
        }
        author
      }
      sort
    }
  }
}
```

2.查询首页书类
>父类及子类展展开；
>本站对应子类下的书籍作品数目展示;
>限制子类数目
```js
query getBookTypeList($rootId: Int=0, $totalCount: Int=12){
  bookTypeList(parentTypeId: $rootId){
    typeId
    typeName
    children(totalCount: $totalCount){
      typeId
      typeName
      parentTypeId
      bookCount
    }
  }
}
```

#### Mutation
1.添加小说
>通过调用此API，作者可以上传自己的作品
```js
mutation addBookMutation($bookName: String!, $author: String, $bookTypeId: Int, $wordNumbers: Int, $cover: String, $banner: String, $summary: String, $status: Int = 0, $tags: String!, $siteId: Int = 1, $xbookId: String, $lastupdate: String) {
  addBook(input: {bookName: $bookName, summary: $summary, author: $author, bookTypeId: $bookTypeId, clickTimes: 0, wordNumbers: $wordNumbers, cover: $cover, banner: $banner, status: $status, tags: $tags, siteId: $siteId, xbookId: $xbookId, lastupdate: $lastupdate}) {
    book {
      bookId
      bookName
      summary
    }
  }
}

query variables
{
  "bookName": "孺子帝",
  "author": "冰临神下",
  "bookTypeId": 11,
  "wordNumbers":1803100,
  "cover": "https://qidian.qpic.cn/qdbimg/349573/1003242530/180",
  "banner": "https://qidian.qpic.cn/qidian_common/349573/78ae3e1422bdb93409a65224a6005b13/0",
  "summary": "三位皇帝接连驾崩，从来没人注意过的皇子莫名其妙地继位，身陷重重危险之中。太后不喜欢他，时刻想要再立一名更年幼、更听话的新皇帝；同父异母的兄弟不喜欢他，认为他夺走了本属于自己的皇位；太监与宫女们也不喜欢他，觉得他不像真正的皇帝……孺子帝唯有自救。",
  "status": 1,
  "tags": "坚毅|强者回归|豪门",
  "siteId": 1,
  "xbookId": "1003242530",
  "lastupdate": "2017-01-12 19:18:58"
}

```
2.添加排行
>小说首页信息调整
```js
mutation addRankMutation($bookId: Int, $rankTypeId: Int, $siteTypeId: Int) {
  addRank(input: {bookId: $bookId, rankTypeId: $rankTypeId, siteId: $siteTypeId}) {
    rank {
      rankId
    }
  }
}

query variables
{
  "bookId": 1,
  "rankTypeId": 2,
  "siteTypeId": 3
}
```

### 四、爬虫相关

我们默认：项目顺利部署，有一定Redis基础。
任务开始后会将Redis中爬到的数据归档到MariaDB。

1.（主服务器）在Redis中执行
```
sadd spider.all https://www.qidian.com/book/coverrec?page=1
lpush spider.wait https://www.qidian.com/book/coverrec?page=1
```

大约几分钟spider.wait队列中就会产生两万条请求

2.所有服务器均通过访问  www.yourdomain.com/missionStart 启动任务

通过修改views.py 自定义线程数。

3.查看执行归档到数据库命令的作品数
`scard save.all`

4.查看执行错误数
```
scard error.spider
scard error.save
```

5.查看日志 vim /home/web/JulyNovel/logs/uwsgi.log

6.爬虫任务完成后，访问 www.yourdomain.com/uploadAll 将源站点的作品相关图片上传到阿里云对象存储。