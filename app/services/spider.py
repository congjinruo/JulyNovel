from .spider_qidian import QidianSpider
from .save import Save
import time
import threading
class Spider:

    def __init__(self, siteId = 1):
        self.siteId = siteId

    def run(self):
        """
        任务开始
        """  
        if self.siteId == 1:
            self.spider = QidianSpider()
            i = 0
            while(i < 30000):
                i += 1
                start = time.time()
                request_url = self.spider.mRedis.keepRequest()
                try:
                    if request_url is None:
                        continue
                    if 'www.qidian.com/book/coverrec' in request_url:
                        self.spider.queryBannerList(request_url)
                    if 'book.qidian.com/info' in request_url:
                        self.spider.queryBookInfo(request_url)
                    if 'qidian.com/chapter' in request_url:
                        self.spider.queryContent(request_url)
                    end = time.time()
                    print("%s 抓取完毕！消耗 %0.2f 秒" % (request_url, end-start))
                except Exception as e:
                    self.spider.addError(request_url)
                    print("%s 抓取出错，堆栈消息：%s" % (request_url, str(e).strip()))

        if self.siteId == 2:
            pass

        print('Spider Mission Ended')

    def insert(self):
        """
        将数据插入MariaDB中
        """
        if self.siteId == 1:
            self.save = Save()
            i = 0
            while(i < 300000):
                i += 1
                start = time.time()
                book = self.save.mRedis.getBook()
                if not book:
                    continue
                try:
                    print("MariaDB Insert Start")
                    self.save.addBook(book)
                except Exception as e:
                    self.save.addError(book["xbookId"])
                    print("《%s》 归档出错，堆栈消息：%s" % (book["bookName"],  str(e).strip()))
                finally:
                    self.save.session.close()
                end = time.time()
                print("《%s》 归档完毕！消耗 %0.2f 秒" % (book["bookName"], end-start))
        if self.siteId == 2:
            pass
        print("MariaDB Insert End")


    def timerStart(self):
        self.save = Save()
        try:
            self.timer = threading.Timer(20, self.checkFinish)
            self.timer.start()
        except Exception as e:
            print(" 校验book出错，堆栈消息：%s"  %  str(e).strip())       

    def checkFinish(self):
        """
        校验book爬取是否完整
        """
        try:
            self.save.checkFinish()
        except Exception as e:
            print(" 校验book出错，堆栈消息：%s" %  str(e).strip())
        
        self.timer = threading.Timer(120, self.checkFinish)
        self.timer.start()
