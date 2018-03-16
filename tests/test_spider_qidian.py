# -*- coding: utf-8 -*-

import unittest
from app.services.spider_qidian import QidianSpider
class TestSpider(unittest.TestCase):

    def test_init(self):
        spider = QidianSpider()
        self.assertTrue(isinstance(spider, QidianSpider))

    def test_query_book_list(self):
        spider = QidianSpider()
        count = spider.queryBookList("https://www.qidian.com/all?orderId=&style=2&pageSize=50&siteid=1&pubflag=0&hiddenField=0&page=1")
        self.assertEqual(count, 50)     

    def test_chapter_api(self):
        spider = QidianSpider()
        chapters = spider.queryChapterApi("107580")
        self.assertEqual(len(chapters), 2600)
        self.assertEqual(chapters[2583]["chapterName"], "第十一卷 真仙降临 第两千四百四十六章 飞升仙界(大结局）")
        self.assertEqual(chapters[2583]["xchapterId"], "48169888")
        self.assertEqual(chapters[2583]["wordNumbers"], "3288")
        self.assertEqual(chapters[2583]["updatetime"], "2013-09-23 22:10:37")
        self.assertEqual(chapters[2583]["free"], 0)
        self.assertEqual(chapters[2583]["xbookId"], "107580")

    def test_query_book_info(self):
        spider = QidianSpider()
        book = spider.queryBookInfo("https://book.qidian.com/info/107580")

        self.assertEqual(book["bookName"] , "凡人修仙传")
        self.assertEqual(book["cover"] , "https://qidian.qpic.cn/qdbimg/349573/107580/180")
        self.assertEqual(book["wordNumbers"], "744.75")
        self.assertEqual(book["author"], "忘语")
        self.assertEqual(book["tags"], "")
        self.assertEqual(book["xbookId"], "107580")
        self.assertEqual(book["status"], 0)
        self.assertEqual(book["lastupdate"], "2016-01-05 17:02:39")

        book_b = spider.queryBookInfo("https://book.qidian.com/info/1010626574")

        self.assertEqual(book_b["bookName"] , "无限刷钱系统")
        self.assertEqual(book_b["cover"] , "https://qidian.qpic.cn/qdbimg/349573/1010626574/180")
        self.assertEqual(book_b["wordNumbers"], "89.21")
        self.assertEqual(book_b["author"], "二发凉了")
        self.assertEqual(book_b["tags"], "明星|爆笑|系统流|赚钱")
        self.assertEqual(book_b["xbookId"], "1010626574")
        self.assertEqual(book_b["status"], 1)
        self.assertEqual(book_b["lastupdate"], "2018-03-16 17:17:32")

    def test_query_content(self):
        spider = QidianSpider()
        content = spider.queryContent("https://read.qidian.com/chapter/_khZq99sDTj7X4qr8VpWrA2/yocLiS1ZCjPM5j8_3RRvhw2")
        print(content)
        self.assertEqual(content["wordNumbers"], '2707')
        self.assertEqual(content["xchapterId"], 'yocLiS1ZCjPM5j8_3RRvhw2')
        self.assertEqual(content["xbookId"], '1010626574')
