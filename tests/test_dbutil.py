# -*- coding: utf-8 -*-

import unittest
from app.utils.operate_db import DBUtil
class TestDBUtil(unittest.TestCase):

    def test_init(self):
        db = DBUtil()
        self.assertTrue(isinstance(db, DBUtil))

    def test_is_book_saved(self):
        db = DBUtil()
        self.assertEqual(db.is_book_saved(xbook_id='1007994514'), True)
        self.assertEqual(db.is_book_saved(book_name='飞剑问道'), True)

        self.assertEqual(db.is_book_saved(xbook_id='??'), False)
        self.assertEqual(db.is_book_saved(book_name='??'), False)

    def test_is_chapter_saved(self):
        db = DBUtil()
        self.assertEqual(db.is_chapter_saved(xchapter_id='7lqcoydR9AdMs5iq0oQwLQ2'), True)
        self.assertEqual(db.is_chapter_saved(chapter_name='第237章 渡鸟之爪', xbook_id='1007994514'), True)

        self.assertEqual(db.is_chapter_saved(xchapter_id='??'), False)
        self.assertEqual(db.is_chapter_saved(chapter_name='??', xbook_id='1007994514'), False)
        self.assertEqual(db.is_chapter_saved(chapter_name='??', xbook_id='??'), False)
    
    def test_is_free_chapter(self):
        db = DBUtil()
        self.assertEqual(db.is_free_chapter(xchapter_id='7lqcoydR9AdMs5iq0oQwLQ2'), True)
        self.assertEqual(db.is_free_chapter(chapter_name='上架感言', xbook_id='1007994514'), True)

        self.assertEqual(db.is_free_chapter(xchapter_id='378925041'), False)
        self.assertEqual(db.is_free_chapter(chapter_name='第237章 渡鸟之爪', xbook_id='1007994514'), False)

        self.assertEqual(db.is_free_chapter(xchapter_id='??'), False)
        self.assertEqual(db.is_free_chapter(chapter_name='??', xbook_id='1007994514'), False)
        self.assertEqual(db.is_free_chapter(chapter_name='??', xbook_id='??'), False)