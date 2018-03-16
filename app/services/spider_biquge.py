import urllib, time, datetime, json, base64, urllib.request, re
from urllib import parse
from bs4 import BeautifulSoup
from ..utils.operate_redis import MRedis
class BiqugeSpider:
    """
    笔趣阁
    仅限学习用途，侵删。
    congjinruo@outlook.com
    """
    def __init__(self):
        """
        siteId: data from
        """
        self.siteId = 4
        self.headers =  {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) \
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36'}
        self.mRedis = MRedis(self.siteId)
    