"""
Book Schema 包含Mutation等各种方法
"""
import graphene
from datetime import datetime
from graphene_sqlalchemy import SQLAlchemyObjectType
from ..data.base import db_session
from ..data.base import Book as BookModel
from .schema_book_type import BookType, BookTypeModel

# Create a generic class to mutualize description of book attributes for both queries and mutations
class BookAttribute:
    book_id = graphene.ID(description="书ID")
    book_name = graphene.String(description="书名")
    summary = graphene.String(description="小说简介")
    book_type_id = graphene.Int(description="书类 ID")
    author = graphene.String(description="作者")
    click_times = graphene.Int(description="本站点击量")
    word_numbers = graphene.Int(description="字数")
    cover = graphene.String(description="作品封面URL地址")
    banner = graphene.String(description="作品轮播图URL地址")
    status = graphene.Int(description="1：完结 ，0 ：连载")
    tags = graphene.String(description="作品标签ID集合。多个以 | 分割")
    site_id = graphene.Int(description="来源站点 id")
    xbook_id = graphene.String(description="来源站点的BOOKID")
    lastupdate = graphene.String(description="最后更新时间")
    file_url = graphene.String(description="生成的TXT文件地址") 


class Book(SQLAlchemyObjectType):
    """Book node."""

    class Meta:
        model = BookModel
        interfaces = (graphene.relay.Node,)
    bookType = graphene.Field(BookType)
    def resolve_bookType(self, info):
        query = BookType.get_query(info)
        # pylint: disable=no-member 
        return query.filter(BookTypeModel.type_id==self.book_type_id).first()


class AddBookInput(graphene.InputObjectType, BookAttribute):
    """Arguments to create a Book."""
    pass


class AddBook(graphene.Mutation):
    """Mutation to create a book."""
    book = graphene.Field(lambda: Book, description="添加作品")

    class Arguments:
        input = AddBookInput(required=True)

    def mutate(self, info, input):
        input['createtime'] = datetime.now()        
        # pylint: disable=no-member        
        book = BookModel(**input)
        db_session.add(book)
        db_session.commit()

        return AddBook(book=book)


class UpdateBookInput(graphene.InputObjectType, BookAttribute):
    """Arguments to update a book."""
    book_id = graphene.ID(required=True, description="Global Id of the book.")


class UpdateBook(graphene.Mutation):
    """Update a book."""
    book = graphene.Field(lambda: Book, description="book updated by this mutation.")

    class Arguments:
        input = UpdateBookInput(required=True)

    def mutate(self, info, input):
        # pylint: disable=no-member
        book = Book.get_query(info).filter(BookModel.book_id==input.get('book_id'))
        book.update(input)
        db_session.commit()
        book = Book.get_query(info).filter(BookModel.book_id==input.get('book_id')).first()

        return UpdateBook(book=book)