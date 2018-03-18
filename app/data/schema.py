"""
Graphene 核心类   Query And Mutation入口
"""
# -*- coding: utf-8 -*-
import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyConnectionField, SQLAlchemyObjectType
from ..data.base import db_session
from .schema_model import Book, BookModel, AddBook, UpdateBook
from .schema_model import BookType, BookTypeModel, AddBookType, UpdateBookType
from .schema_model import Rank, RankModel, AddRank, UpdateRank
from .schema_model import RankType, RankTypeModel, AddRankType, UpdateRankType
from .schema_model import Chapter, ChapterModel, AddChapter, UpdateChapter
from .schema_model import Content, ContentModel, AddContent, UpdateContent
from sqlalchemy import and_, or_, case

"""
GraphQL查询
"""
class Query(graphene.ObjectType):
    """The query root of JulyNovel's GraphQL interface."""
    node = relay.Node.Field()
    # Book
    book = graphene.Field(lambda: Book, bookId=graphene.ID())
    bookList = SQLAlchemyConnectionField(lambda: Book, bookTypeId=graphene.ID(), search=graphene.String())

    def resolve_book(self, info, bookId):
        query = Book.get_query(info).get(bookId)
        # pylint: disable=no-member 
        db_session.execute("UPDATE BOOK SET CLICK_TIMES = %s WHERE BOOK_ID = %s " % (query.click_times + 1, bookId))
        db_session.commit()
        return query

    def resolve_bookList(self, info, **args):
        query = Book.get_query(info)
        if args.get('bookTypeId') is not None:
            if args.get('bookTypeId') == -1:
                return query
            elif args.get('bookTypeId') in [1, 2, 3]:
                typeQuery = BookType.get_query(info).filter(BookTypeModel.parent_type_id==args.get('bookTypeId')).all()
                type_id_children = []
                for bookType in typeQuery:
                    type_id_children.append(bookType.type_id)

                query = query.filter(BookModel.book_type_id.in_(type_id_children)).order_by(BookModel.createtime.desc())
            else:
                query = query.filter(BookModel.book_type_id==args.get('bookTypeId')).order_by(BookModel.createtime.desc()).all()
        elif args.get('search') is not None:
            #query = query.filter(or_(BookModel.book_name.like('%%%s%%' % args.get('search')), BookModel.author.like('%%%s%%' % args.get('search')))).all()
            bookList_a = query.filter(BookModel.book_name.like('%%%s%%' % args.get('search'))).all()
            bookList_b =query.filter(BookModel.author.like('%%%s%%' % args.get('search'))).all()
            bookList_c = [] + bookList_a
            for x in bookList_a:
                for y in bookList_b:
                    if x.book_id != y.book_id:
                        bookList_c.append(y)
            return bookList_c
        return query

    #Chapter
    chapter = graphene.Field(lambda: Chapter, chapterId=graphene.ID())

    def resolve_chapter(self, info, chapterId):
        return Chapter.get_query(info).get(chapterId)

    #Content
    content = graphene.Field(lambda: Content, chapterId=graphene.ID())

    def resolve_content(self, info, chapterId):
        query = Content.get_query(info).filter(ContentModel.chapter_id==chapterId).first()
        return query

    # BookType
    bookType = graphene.Field(lambda: BookType, typeId=graphene.ID())
    bookTypeList = graphene.List(lambda: BookType, parentTypeId=graphene.Int())

    def resolve_bookType(self, info, **args):
        query = BookType.get_query(info)
        if args.get('typeId') is not None:
            query = query.filter(BookTypeModel.type_id==args.get('typeId'))
        return query.first()
    def resolve_bookTypeList(self, info, **args):
        query = BookType.get_query(info)
        if args.get('parentTypeId') is not None:
            query = query.filter(BookTypeModel.parent_type_id==args.get('parentTypeId'))
        return query
    #rank
    rank = graphene.Field(lambda:Rank, rankId=graphene.ID())
    rankList = SQLAlchemyConnectionField(lambda:Rank, rankTypeId=graphene.Int())

    def resolve_rank(self, info, **args):
        query = Rank.get_query(info)
        if args.get('rankId') is not None:
            query = query.filter(RankModel.rank_type_id==args.get('rankId')).first()
        return query

    def resolve_rankList(self, info,  **args):
        query = Rank.get_query(info)
        if args.get('rankTypeId')  is not None:
            query = query.filter(RankModel.rank_type_id==args.get('rankTypeId'))
        return query.order_by(RankModel.sort.desc())

    #rankType
    rankType = graphene.Field(lambda:RankType, rankTypeId=graphene.ID())
    rankTypeList = SQLAlchemyConnectionField(lambda:Rank)
    homeRankList = graphene.List(lambda: RankType)

    def resolve_rankType(self, info, **args):
        query = RankType.get_query(info)
        if args.get('rankTypeId') is not None:
            query = query.filter(RankTypeModel.type_id==args.get('rankTypeId')).first()
        return query

    def resolve_homeRankList(self, info):
        query = RankType.get_query(info)
        return query.filter(RankTypeModel.state==1).all()
     

class Mutation(graphene.ObjectType):
    """The mutation root of JulyNovel's GraphQL interface."""
    # book mutation
    addBook = AddBook.Field()
    updateBook = UpdateBook.Field()
    #bookType mutation
    addBookType = AddBookType.Field()
    updateBookType = UpdateBookType.Field()
    #rank mutation
    addRank = AddRank.Field()
    updateRank  = UpdateRank.Field()
    #rankType mutation
    addRankType = AddRankType.Field()
    updateRankType  = UpdateRankType.Field()
    #chapter mutation
    addChapter = AddChapter.Field()
    updateChapter = UpdateChapter.Field()
    #content mutation
    addContent = AddContent.Field()
    updateContent = UpdateContent.Field()

    
schema = graphene.Schema(query=Query, mutation=Mutation)