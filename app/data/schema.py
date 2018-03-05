"""
Graphene 核心类   Query And Mutation入口
"""
# -*- coding: utf-8 -*-
import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyConnectionField, SQLAlchemyObjectType
from ..data.base import db_session
from ..models.schema_book import Book, BookModel, AddBook, UpdateBook
from ..models.schema_book_type import BookType, BookTypeModel, AddBookType, UpdateBookType
from ..models.schema_rank import Rank, RankModel, AddRank, UpdateRank
from ..models.schema_rank_type import RankType, RankTypeModel, AddRankType, UpdateRankType
from sqlalchemy import and_
from app import cache
"""
GraphQL查询
"""
class Query(graphene.ObjectType):
    """The query root of JulyNovel's GraphQL interface."""
    node = relay.Node.Field()
    # Book
    book = graphene.Field(Book, bookId=graphene.ID())
    bookList = SQLAlchemyConnectionField(Book)

    def resolve_book(self, info, bookId):
        query = Book.get_query(info)
        return query.filter(BookModel.book_id==bookId).first()

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
        #rank
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
    
schema = graphene.Schema(query=Query, mutation=Mutation)