一、添加小说
```js
mutation addBookMutation($bookName: String!, $author: String, $bookTypeId: Int, $wordNumbers: Int, $cover: String, $banner: String, $summary: String, $status: Int = 0, $tags: String!, $siteId: Int = 1, $xbookId: String, $lastupdate: String) {
  addBook(input: {bookName: $bookName, summary: $summary, author: $author, bookTypeId: $bookTypeId, clickTimes: 0, wordNumbers: $wordNumbers, cover: $cover, banner: $banner, status: $status, tags: $tags, siteId: $siteId, xbookId: $xbookId, lastupdate: $lastupdate}) {
    book {
      bookId
      bookName
      summary
    }
  }
}

query variables
{
  "bookName": "孺子帝",
  "author": "冰临神下",
  "bookTypeId": 11,
  "wordNumbers":1803100,
  "cover": "https://qidian.qpic.cn/qdbimg/349573/1003242530/180",
  "banner": "https://qidian.qpic.cn/qidian_common/349573/78ae3e1422bdb93409a65224a6005b13/0",
  "summary": "三位皇帝接连驾崩，从来没人注意过的皇子莫名其妙地继位，身陷重重危险之中。太后不喜欢他，时刻想要再立一名更年幼、更听话的新皇帝；同父异母的兄弟不喜欢他，认为他夺走了本属于自己的皇位；太监与宫女们也不喜欢他，觉得他不像真正的皇帝……孺子帝唯有自救。",
  "status": 1,
  "tags": "坚毅|强者回归|豪门",
  "siteId": 1,
  "xbookId": "1003242530",
  "lastupdate": "2017-01-12 19:18:58"
}

```
二、添加排行
```js
mutation addRankMutation($bookId: Int, $rankTypeId: Int, $siteTypeId: Int) {
  addRank(input: {bookId: $bookId, rankTypeId: $rankTypeId, siteId: $siteTypeId}) {
    rank {
      rankId
    }
  }
}

query variables
{
  "bookId": 1,
  "rankTypeId": 2,
  "siteTypeId": 3
}
```
