"""
RankType Schema
"""
# -*- coding: utf-8 -*-
import graphene
from datetime import datetime
from graphene_sqlalchemy import SQLAlchemyObjectType
from ..data.base import db_session
from ..data.base import RankType as RankTypeModel
from .schema_rank import Rank, RankModel


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