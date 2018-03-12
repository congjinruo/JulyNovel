"""
Model Schema 包含Mutation等各种方法
"""
import graphene
from datetime import datetime
from graphene_sqlalchemy import SQLAlchemyObjectType
from .base import db_session
from .base import Book as BookModel
from .base import BookType as BookTypeModel
from .base import Chapter as ChapterModel
from .base import Content as ContentModel
from .base import RankType as RankTypeModel
from .base import Rank as RankModel


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

class BookType(SQLAlchemyObjectType):
    """BookType node."""

    class Meta:
        model = BookTypeModel
        interfaces = (graphene.relay.Node,)
    children = graphene.List(BookTypeChildren, totalCount=graphene.Int())
    recommends = graphene.List(lambda: Book, bookId=graphene.ID())
    totalBookCount = graphene.Int()
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

    def resolve_recommends(self, info, **args):
        # pylint: disable=no-member
        query = Book.get_query(info)
        if args.get('bookId') is not None:
            print(1)
            query = query.filter(BookModel.book_type_id==self.type_id, ~(BookModel.book_id==args.get('bookId')))
        else:
            print(0)
            query = query.filter(BookModel.book_type_id==self.type_id)
        query = query.order_by(BookModel.createtime.desc()).limit(6)
        return query

    def resolve_totalBookCount(self, info):
        # pylint: disable=no-member
        if self.type_id == -1:
            count = db_session.execute("SELECT COUNT(BOOK_TYPE_ID) FROM BOOK ").scalar()
        elif self.type_id in [1, 2, 3]:
            typeQuery = BookType.get_query(info).filter(BookTypeModel.parent_type_id==self.type_id).all()
            type_id_children = []            
            for bookType in typeQuery:
                print(str(bookType.type_id))   
                type_id_children.append(str(bookType.type_id))
            ids =  ','.join(type_id_children)
            count =  db_session.execute("SELECT COUNT(BOOK_TYPE_ID) FROM BOOK WHERE BOOK_TYPE_ID in (%s)" %  ids).scalar()
        else:
            count = db_session.execute("SELECT COUNT(BOOK_TYPE_ID) FROM BOOK WHERE BOOK_TYPE_ID = " + str(self.type_id)).scalar()
        if count is None:
            return 0
        return count
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
    chapterList = graphene.List(lambda:Chapter, totalCount=graphene.Int())

    def resolve_chapterList(self, info, **args):
        # pylint: disable=no-member 
        query = Chapter.get_query(info).filter(ChapterModel.book_id==self.book_id)
        query = query.order_by(ChapterModel.sort.asc()).all()
        return query
    def resolve_bookType(self, info):
        query = BookType.get_query(info)
        # pylint: disable=no-member 
        return query.get(self.book_type_id)


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



# Create a generic class to mutualize description of chapter attributes for both queries and mutations
class ChapterAttribute:
    chapter_id = graphene.ID(description="章节ID")
    chapter_name = graphene.String(description="章节名")
    book_id = graphene.Int(description="所属作品id")
    word_numbers = graphene.Int(description="字数")
    volume_id = graphene.Int(description="卷id")
    free = graphene.Int(description="1 为免费 0为收费")
    sort = graphene.Int(description="章节排序")
    xchapter_id = graphene.String(description="来源站点的章节id")
    updatetime = graphene.String(description="更新时间")


class Chapter(SQLAlchemyObjectType):
    """Chapter node."""

    class Meta:
        model = ChapterModel
        interfaces = (graphene.relay.Node,)
    content = graphene.Field(lambda: Content)
    book = graphene.Field(lambda: Book)
    prevChapterId = graphene.ID()
    nextChapterId = graphene.ID()
    def resolve_content(self, info):
        # pylint: disable=no-member
        query = Content.get_query(info).filter(ContentModel.chapter_id==self.chapter_id).first()
        return query
    def resolve_book(self, info):
        # pylint: disable=no-member
        query = Book.get_query(info).get(self.book_id)
        return query
    def resolve_prevChapterId(self, info):
         # pylint: disable=no-member
         if self.sort == 1:
             return None
         query = Chapter.get_query(info).filter(ChapterModel.sort==(self.sort - 1), ChapterModel.book_id==self.book_id).first()
         return query.chapter_id

    def resolve_nextChapterId(self, info):
         # pylint: disable=no-member
         query = Chapter.get_query(info).filter(ChapterModel.sort==(self.sort + 1), ChapterModel.book_id==self.book_id).first()
         if query is None:
             return None
         return query.chapter_id
    
class AddChapterInput(graphene.InputObjectType, ChapterAttribute):
    """Arguments to create a Chapter."""
    pass


class AddChapter(graphene.Mutation):
    """Mutation to create a chapter."""
    chapter = graphene.Field(lambda: Chapter, description="添加章节")

    class Arguments:
        input = AddChapterInput(required=True)

    def mutate(self, info, input):
        input['createtime'] = datetime.now()        
        # pylint: disable=no-member        
        chapter = ChapterModel(**input)
        db_session.add(chapter)
        db_session.commit()

        return AddChapter(chapter=chapter)


class UpdateChapterInput(graphene.InputObjectType, ChapterAttribute):
    """Arguments to update a chapter."""
    chapter_id = graphene.ID(required=True, description="Global Id of the chapter.")


class UpdateChapter(graphene.Mutation):
    """Update a chapter."""
    chapter = graphene.Field(lambda: Chapter, description="chapter updated by this mutation.")

    class Arguments:
        input = UpdateChapterInput(required=True)

    def mutate(self, info, input):
        # pylint: disable=no-member
        chapter = Chapter.get_query(info).filter(ChapterModel.chapter_id==input.get('chapter_id'))
        chapter.update(input)
        db_session.commit()
        chapter = Chapter.get_query(info).filter(ChapterModel.chapter_id==input.get('chapter_id')).first()

        return UpdateChapter(chapter=chapter)


# Create a generic class to mutualize description of content attributes for both queries and mutations
class ContentAttribute:
    content_id = graphene.ID(description="内容ID")
    chapter_id = graphene.ID(description="所属章节id")
    text = graphene.String(description="内容")
    book_id = graphene.ID(description="所属作品id")
    word_numbers = graphene.Int(description="字数")


class Content(SQLAlchemyObjectType):
    """Content node."""

    class Meta:
        model = ContentModel
        interfaces = (graphene.relay.Node,)


class AddContentInput(graphene.InputObjectType, ContentAttribute):
    """Arguments to create a Content."""
    pass


class AddContent(graphene.Mutation):
    """Mutation to create a content."""
    content = graphene.Field(lambda: Content, description="添加作品")

    class Arguments:
        input = AddContentInput(required=True)

    def mutate(self, info, input):
        input['createtime'] = datetime.now()        
        # pylint: disable=no-member        
        content = ContentModel(**input)
        db_session.add(content)
        db_session.commit()

        return AddContent(content=content)


class UpdateContentInput(graphene.InputObjectType, ContentAttribute):
    """Arguments to update a content."""
    content_id = graphene.ID(required=True, description="Global Id of the content.")


class UpdateContent(graphene.Mutation):
    """Update a content."""
    content = graphene.Field(lambda: Content, description="content updated by this mutation.")

    class Arguments:
        input = UpdateContentInput(required=True)

    def mutate(self, info, input):
        # pylint: disable=no-member
        content = Content.get_query(info).filter(ContentModel.content_id==input.get('content_id'))
        content.update(input)
        db_session.commit()
        content = Content.get_query(info).filter(ContentModel.content_id==input.get('content_id')).first()

        return UpdateContent(content=content)


# Create a generic class to mutualize description of book attributes for both queries and mutations
class RankTypeAttribute:
    type_id = graphene.ID(description="排行榜类别 ID")
    type_name = graphene.String(description="排行榜类别名称")
    display_count = graphene.Int(description="默认展示数目")
    site_id = graphene.Int(description="类别来源站点")
    state = graphene.Int(description="是否启用：1 启用 0 停用")

class RankType(SQLAlchemyObjectType):
    """RankType node."""

    class Meta:
        model = RankTypeModel
        interfaces = (graphene.relay.Node,)
    rankList = graphene.List(lambda:Rank, totalCount=graphene.Int())
    def resolve_rankList(self, info, **args):
        # pylint: disable=no-member  
        query = Rank.get_query(info)
        query = query.filter(RankModel.rank_type_id==self.type_id).order_by(RankModel.sort.desc())
        if args.get('totalCount') is not None:
            query = query.limit(args.get('totalCount'))
        if self.display_count is not None:
            query = query.limit(self.display_count)       
        return query

class AddRankTypeInput(graphene.InputObjectType, RankTypeAttribute):
    """Arguments to create  RankType."""
    pass


class AddRankType(graphene.Mutation):
    """Mutation to create a book."""
    rankType = graphene.Field(lambda: RankType, description="添加排行榜")

    class Arguments:
        input = AddRankTypeInput(required=True)

    def mutate(self, info, input):
        """scope_session动态生成add、commit方法，pylint提示错误。  """
        if input.get('state') is None:
            input['state'] = 1
        input['createtime'] = datetime.now()
        rankType = RankTypeModel(**input)
        # pylint: disable=no-member  
        db_session.add(rankType)
        db_session.commit()

        return AddRankType(rankType=rankType)


class UpdateRankTypeInput(graphene.InputObjectType, RankTypeAttribute):
    """Arguments to update  rankType."""
    type_id = graphene.ID(required=True, description="Global Id of the rankType.")


class UpdateRankType(graphene.Mutation):
    """Update  rankType."""
    rankType = graphene.Field(lambda: RankType, description="rankType updated by this mutation.")

    class Arguments:
        input = UpdateRankTypeInput(required=True)

    def mutate(self, info, input):
        rankType = RankType.get_query(info).filter(RankTypeModel.type_id==input.get('type_id'))
        rankType.update(input)
        # pylint: disable=no-member
        db_session.commit()
        rankType = RankType.get_query(info).filter(RankTypeModel.type_id==input.get('type_id')).first()

        return UpdateRankType(rankType=rankType)


# Create a generic class to mutualize description of book attributes for both queries and mutations
class RankAttribute:
    rank_id = graphene.ID(description="排行榜 ID")
    book_id = graphene.Int(description="书名")
    rank_type_id = graphene.Int(description="排行榜类别 id")
    sort = graphene.Int(description="排行榜排序")
    site_id = graphene.Int(description="来源站点")
    state = graphene.Int(description="是否启用")  


class Rank(SQLAlchemyObjectType):
    """Rank node."""

    class Meta:
        model = RankModel
        interfaces = (graphene.relay.Node,)
    book = graphene.Field(Book)
    def resolve_book(self, info):      
        query = Book.get_query(info)
        # pylint: disable=no-member
        query = query.get(self.book_id)
        if self.rank_type_id not in [2, 4, 5]:
            query.summary = ""
        return query
class AddRankInput(graphene.InputObjectType, RankAttribute):
    """Arguments to create  Rank."""
    pass


class AddRank(graphene.Mutation):
    """Mutation to create a book."""
    rank = graphene.Field(lambda: Rank, description="添加排行榜")

    class Arguments:
        input = AddRankInput(required=True)

    def mutate(self, info, input):
        """scope_session动态生成add、commit方法，pylint提示错误。  """
        if input.get('state') is None:
            input['state'] = 1
        input['createtime'] = datetime.now()
        rank = RankModel(**input)
        # pylint: disable=no-member  
        db_session.add(rank)
        db_session.commit()

        return AddRank(rank=rank)


class UpdateRankInput(graphene.InputObjectType, RankAttribute):
    """Arguments to update  rank."""
    rank_id = graphene.ID(required=True, description="Global Id of the rank.")


class UpdateRank(graphene.Mutation):
    """Update  rank."""
    rank = graphene.Field(lambda: Rank, description="rank updated by this mutation.")

    class Arguments:
        input = UpdateRankInput(required=True)

    def mutate(self, info, input):
        rank = Rank.get_query(info).filter(RankModel.rank_id==input.get('rank_id'))
        rank.update(input)
        # pylint: disable=no-member
        db_session.commit()
        rank = Rank.get_query(info).filter(RankModel.rank_id==input.get('rank_id')).first()

        return UpdateRank(rank=rank)