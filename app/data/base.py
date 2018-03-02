"""
ORM 构建对象
"""
# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from config import Config

from sqlalchemy import Column, DateTime, Integer, Text, func, String

engine = create_engine(Config.MARIADB_SERVER, encoding="utf-8", echo=False)

db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()

Base.query = db_session.query_property()


"""爬虫相关"""
class SourceSite(Base):
    """源站点"""
    __tablename__ = 'SOURCE_SITE'
    site_id = Column(Integer, primary_key=True)
    site_name = Column(String(255))
    site_url = Column(String(255))
    state = Column(Integer)
    createtime = Column(DateTime)

class SpiderRule(Base):
    """爬虫策略表"""
    __tablename__ = 'SPIDER_RULE'
    rule_id = Column(Integer, primary_key=True)
    rule_name = Column(String(255))
    rule_url = Column(String(255))
    res_url = Column(String(255))
    rule_type = Column(Integer)
    site_id = Column(Integer)
    state = Column(Integer)
    createtime = Column(DateTime)


"""排行榜相关"""
class RankType(Base):
    """各大排行"""
    __tablename__ = 'RANK_TYPE'
    type_id = Column(Integer, primary_key=True)
    type_name = Column(String(255))
    site_id = Column(Integer)
    state = Column(Integer)
    createtime = Column(DateTime)

class Rank(Base):
    """排行榜"""
    __tablename__ = 'RANK'
    rank_id = Column(Integer, primary_key=True)
    book_id = Column(Integer)
    rank_type_id = Column(Integer)
    sort = Column(Integer)
    site_id = Column(Integer)
    state = Column(Integer)
    createtime = Column(DateTime)   


"""作品相关"""
class BookType(Base):
    """作品类别"""
    __tablename__ = 'BOOK_TYPE'
    type_id = Column(Integer, primary_key=True)
    type_name = Column(String(255))
    summary = Column(String(255))
    parent_type_id = Column(Integer)
    state = Column(Integer)
    createtime = Column(DateTime)

class BookTag(Base):
    """作品标签"""
    __tablename__ = 'BOOK_TAG'
    tag_id = Column(Integer, primary_key=True)
    tag_name =  Column(String(255))
    state = Column(Integer)
    createtime = Column(DateTime)

class Book(Base):
    """作品"""
    __tablename__ = 'BOOK'
    book_id = Column(Integer, primary_key=True)
    book_name = Column(String(255))
    summary = Column(Text)
    book_type_id = Column(Integer)
    author = Column(String(255))
    cover = Column(String(255))
    banner = Column(String(255))    
    click_times = Column(Integer)
    word_numbers = Column(Integer)
    status = Column(Integer)
    tags = Column(String(255))
    site_id = Column(Integer)
    xbook_id = Column(String(255))
    file_url = Column(String(255))
    lastupdate = Column(DateTime)
    createtime = Column(DateTime)

class Volume(Base):
    """作品卷名"""
    __tablename__ = 'VOLUME'
    volume_id = Column(Integer, primary_key=True)
    volume_name  = Column(String(255))
    book_id = Column(Integer)
    createtime = Column(DateTime)

class Chapter(Base):
    """作品章节"""
    __tablename__ = 'CHAPTER'
    chapter_id = Column(Integer, primary_key=True)
    chapter_name = Column(String(255))
    book_id = Column(Integer)
    word_numbers = Column(Integer)
    volume_id = Column(Integer)
    xchapter_id = Column(Integer)
    free = Column(Integer)
    sort = Column(Integer)
    updatetime = Column(DateTime)
    createtime = Column(DateTime)

class Content(Base):
    """章节内容"""
    __tablename__ = 'CONTENT'
    content_id = Column(Integer, primary_key=True)
    chapter_id = Column(Integer)
    text = Column(Text)
    book_id = Column(Integer)
    word_numbers = Column(Integer)
    createtime = Column(DateTime)
