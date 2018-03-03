from datetime import datetime
from graphene.utils import str_converters
from ..utils.operate_redis import MRedis
from ..data.base import db_session
from ..data.base import Book as BookModel, Chapter as ChapterModel, Content as ContentModel, BookType as BookTypeModel

class Save:
    """
    定时将数据归档到MariaDB
    """
    def __init__(self):
        self.mRedis = MRedis()
        self.session = db_session

    def addBook(self, item):
        t = datetime.now()
        item["siteId"] = self.mRedis.siteId
        item["createtime"] = t
        item["clickTimes"] = 0
        item["bookTypeId"] = self.getBookTypeId(item["bookTypeId"])
        item['status'] = int(item['status'])
        if item["wordNumbers"] is not None:
            number = float(item["wordNumbers"])
            if number > 1 :
                item["wordNumbers"] = int(10000*number)
            else:
                item["wordNumbers"] = int(1000*number)
        else:
            item["wordNumbers"] = 0

        book = BookModel(**self.convertField(item))
        # pylint: disable=no-member 
        self.session.add(book)
        self.session.commit()
        self.addChapters(book.xbook_id, book.book_id)

    def addChapters(self, xbookId, bookId):
        items = self.mRedis.getChapterList(xbookId)
        t = datetime.now()
        for item in items:
            item["bookId"] = bookId
            item["createtime"] = t
            item["sort"] = int(item['sort'])
            if item["wordNumbers"] is not None:
                item["wordNumbers"] = int(item["wordNumbers"])
            item.pop("xbookId")
            chapter = ChapterModel(**self.convertField(item))
            # pylint: disable=no-member  
            self.session.add(chapter)
            self.session.commit()
            self.addContent(xbookId, chapter.xchapter_id, bookId, chapter.chapter_id)

    def addContent(self, xbookId, xchapterId, bookId, chapterId):
        item = self.mRedis.getContent(xbookId, xchapterId)
        if not item:
            return
        t = datetime.now()
        item["chapterId"] = chapterId
        item["bookId"] = bookId
        item["createtime"] = t
        item.pop("xbookId")
        item.pop("xchapterId")
        content = ContentModel(**self.convertField(item))
        # pylint: disable=no-member  
        self.session.add(content)
        self.session.commit()


    def getBookTypeId(self, typeName):
        # pylint: disable=no-member  
        bookType = self.session.query(BookTypeModel).filter_by(type_name=typeName).first()
        if bookType is None:
            return -1
        else:
            return bookType.type_id

    def convertField(self, item):
        res = dict()
        for k in item:
            key = str_converters.to_snake_case(k)
            res[key] = item[k]
        return res

    def addError(self, value):
        """
        插入出错，添加错误记录
        """
        self.mRedis.addSaveError(value)


    def checkFinish(self):
        """
        校验完整性
        """
        self.mRedis.checkFinish()



        

