# -*- coding: utf-8 -*-

import unittest
from app.services.spider_biquge import BiqugeSpider

class TestSpider(unittest.TestCase):

    def test_init(self):
        spider = BiqugeSpider()
        self.assertTrue(isinstance(spider, BiqugeSpider))

    def test_query_book_info(self):
        spider = BiqugeSpider()
        book = spider.queryBookInfo("http://www.biquge.com.tw/19_19542/")

        self.assertEqual(book["bookName"] , "量子意志")
        self.assertEqual(book["cover"] , "http://www.biquge.com.tw/files/article/image/19/19542/19542s.jpg")
        self.assertEqual(book["wordNumbers"], None)
        self.assertEqual(book["author"], "十里桃花")
        self.assertEqual(book["tags"], "")
        self.assertEqual(book["xbookId"], "19_19542")
        self.assertEqual(book["status"], 0)
        self.assertEqual(book["lastupdate"], "2018-04-15")

    def test_query_content(self):
        spider = BiqugeSpider()
        content = spider.queryContent("http://www.biquge.com.tw/19_19542/9097996.html")
        print(content)
        self.assertEqual(content["xchapterId"], '9097996')
        self.assertEqual(content["xbookId"], '19_19542')