"""
Content Schema 包含Mutation等各种方法
"""
import graphene
from datetime import datetime
from graphene_sqlalchemy import SQLAlchemyObjectType
from ..data.base import db_session
from ..data.base import Content as ContentModel

# Create a generic class to mutualize description of content attributes for both queries and mutations
class ContentAttribute:
    content_id = graphene.ID(description="内容ID")
    chapter_id = graphene.Int(description="所属章节id")
    text = graphene.String(description="内容")
    book_id = graphene.Int(description="所属作品id")
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