"""
操作Maria DB
"""
# -*- coding: utf-8 -*-
from config import Config
from ..data.base import Book as BookModel
from ..data.base import Chapter as ChapterModel
from ..data.base import db_session
from sqlalchemy import or_, and_

class DBUtil:
    """
    数据库帮助类
    校验各种
    """
    def  is_book_saved(self, **args):
        """
        根据 小说名称/源站点xbook_id 校验书籍是否存在
        """
        # pylint: disable=no-member
        if  args.get("xbook_id"):
            count = db_session.execute("SELECT 1 FROM BOOK WHERE XBOOK_ID = '%s' LIMIT 1" % args.get("xbook_id")).scalar()
        if  args.get("book_name"):
            count = db_session.execute("SELECT 1 FROM BOOK WHERE BOOK_NAME = '%s'  LIMIT 1" % args.get("book_name")).scalar()

        return count == 1

    def is_chapter_saved(self, **args):
        """
        根据 章节名称/源站点xchapter_id 校验章节是否存在
        """
        # pylint: disable=no-member  
        if  args.get("xchapter_id"):
            count = db_session.execute("SELECT 1 FROM CHAPTER WHERE XCHAPTER_ID = '%s' LIMIT 1" % args.get("xchapter_id")).scalar()
        if  args.get("chapter_name") and  args.get("xbook_id"):
            count = db_session.execute("SELECT 1 FROM CHAPTER LEFT JOIN BOOK ON BOOK.BOOK_ID=CHAPTER.BOOK_ID\
             WHERE BOOK.XBOOK_ID='%s' AND  CHAPTER.CHAPTER_NAME = '%s'  LIMIT 1" % (args.get("xbook_id") ,args.get("chapter_name"))).scalar()

        return count == 1

    def is_free_chapter(self, **args):
        # pylint: disable=no-member  
        if  args.get("xchapter_id"):
            free = db_session.execute("SELECT FREE  FROM CHAPTER WHERE  XCHAPTER_ID = '%s'  LIMIT 1" % args.get("xchapter_id")).scalar()
        if  args.get("chapter_name") and  args.get("xbook_id"):
            free = db_session.execute("SELECT CHAPTER.FREE FROM CHAPTER LEFT JOIN BOOK ON BOOK.BOOK_ID=CHAPTER.BOOK_ID\
             WHERE BOOK.XBOOK_ID='%s' AND  CHAPTER.CHAPTER_NAME = '%s'  LIMIT 1" % (args.get("xbook_id") ,args.get("chapter_name"))).scalar()

        return free == 1 or free == 2

    def resort_chapters(self):
        """
        解决sort全为1的问题
        """
        # pylint: disable=no-member
        books = db_session.execute("SELECT BOOK_ID FROM CHAPTER  WHERE SORT = 1 GROUP BY BOOK_ID HAVING COUNT(SORT) > 1").fetchall()
        for book in books:
            chapters = db_session.execute("SELECT CHAPTER_ID FROM CHAPTER WHERE BOOK_ID = %s ORDER BY UPDATETIME ASC " % book["BOOK_ID"]).fetchall()
            i = 0
            for chapter in chapters:
                i += 1
                db_session.execute("UPDATE CHAPTER SET SORT = %s  WHERE CHAPTER_ID = %s" % (i, chapter["CHAPTER_ID"]))
        db_session.commit()

    def add_clicktimes(self):
        pass

    def close(self):
        # pylint: disable=no-member 
        db_session.flush()
        db_session.close()
        db_session.remove()
        print("db_session  removed")


