"""
BookType Schema
"""
# -*- coding: utf-8 -*-
import graphene
from datetime import datetime
from graphene_sqlalchemy import SQLAlchemyObjectType
from ..data.base import db_session
from ..data.base import BookType as BookTypeModel
from app import cache


# Create a generic class to mutualize description of book attributes for both queries and mutations
class BookTypeAttribute:
    type_id = graphene.ID(description="类别ID")
    type_name = graphene.String(description="类别名")
    summary = graphene.String(description="类别简介")
    parent_type_id = graphene.Int(description="父类 ID")
    state = graphene.Int(description="是否启用")

class BookTypeChildren(SQLAlchemyObjectType):
    """BookTypeChildren node."""
    class Meta:
	    model = BookTypeModel
	    interfaces = (graphene.relay.Node, )
    bookCount = graphene.Int()

    def resolve_bookCount(self, info):
         # pylint: disable=no-member
        count = db_session.execute("SELECT COUNT(BOOK_TYPE_ID) FROM BOOK WHERE BOOK_TYPE_ID = " + str(self.type_id)).scalar()
        if count is None:
            return 0
        return count

class BookType(SQLAlchemyObjectType):
    """BookType node."""

    class Meta:
        model = BookTypeModel
        interfaces = (graphene.relay.Node,)
    children = graphene.List(BookTypeChildren, totalCount=graphene.Int())
    def resolve_children(self, info, **args):
        # pylint: disable=no-member
        if self.type_id > 3:
            return None
        else:
            query = BookType.get_query(info).filter(BookTypeModel.parent_type_id==self.type_id)
            if args.get('totalCount') is not None:
                return query.limit(args.get('totalCount'))
            else:
                return query  

class AddBookTypeInput(graphene.InputObjectType, BookTypeAttribute):
    """Arguments to create  BookType."""
    pass


class AddBookType(graphene.Mutation):
    """Mutation to create a book."""
    bookType = graphene.Field(lambda: BookType, description="添加作品类别")

    class Arguments:
        input = AddBookTypeInput(required=True)

    def mutate(self, info, input):
        if input.get('state') is None:
            input['state'] = 1        
        input['createtime'] = datetime.now()        
        bookType = BookTypeModel(**input)
        # pylint: disable=no-member        
        db_session.add(bookType)
        db_session.commit()

        return AddBookType(bookType=bookType)


class UpdateBookTypeInput(graphene.InputObjectType, BookTypeAttribute):
    """Arguments to update  booktype."""
    type_id = graphene.ID(required=True, description="Global Id of the booktype.")


class UpdateBookType(graphene.Mutation):
    """Update  book type."""
    bookType = graphene.Field(lambda: BookType, description="booktype updated by this mutation.")

    class Arguments:
        input = UpdateBookTypeInput(required=True)

    def mutate(self, info, input):
        bookType = BookType.get_query(info).filter(BookTypeModel.type_id==input.get('type_id'))
        bookType.update(input)
        # pylint: disable=no-member
        db_session.commit()
        bookType = BookType.get_query(info).filter(BookTypeModel.type_id==input.get('type_id')).first()

        return UpdateBookType(bookType=bookType)