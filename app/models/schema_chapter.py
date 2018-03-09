"""
Chapter Schema 包含Mutation等各种方法
"""
import graphene
from datetime import datetime
from graphene_sqlalchemy import SQLAlchemyObjectType
from ..data.base import db_session
from ..data.base import Chapter as ChapterModel
from ..data.base import Content as ContentModel

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