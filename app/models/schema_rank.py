"""
Rank Schema
"""
# -*- coding: utf-8 -*-
import graphene
from datetime import datetime
from graphene_sqlalchemy import SQLAlchemyObjectType
from ..data.base import db_session
from ..data.base import Rank as RankModel
from .schema_book import Book, BookModel
from app import cache


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
        return query.filter(BookModel.book_id==self.book_id).first()
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