from ..data.schema import schema
from gql import gql, Client

client = Client(schema=schema)
query = gql('''
query getRankList($rankTypeId: ID = 1, $totalCount: Int = 4, $withBookTypeName: Boolean = false, $withSummary: Boolean = false) {
  rankType(rankTypeId: $rankTypeId) {
    typeId
    typeName
    rankList(totalCount: $totalCount) {
      rankTypeId
      book {
        bookId
        bookName
        cover
        banner
        summary @include(if: $withSummary)
        bookType @include(if: $withBookTypeName) {
          typeName
        }
        author
      }
      sort
    }
  }
}
''')

class Mutation:
    pass

def addBook():
    res = client.execute(query)
    return res

result = addBook()