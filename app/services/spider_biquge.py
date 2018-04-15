import urllib, time, datetime, json, base64, urllib.request, re
from urllib import parse
from bs4 import BeautifulSoup
from ..utils.operate_redis import MRedis
class BiqugeSpider:
    """
    笔趣阁
    仅限学习用途，侵删。
    congjinruo@outlook.com
    """
    def __init__(self):
        """
        siteId: data from
        """
        self.siteId = 4
        self.headers =  {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) \
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36'}
        self.mRedis = MRedis(self.siteId)
    

    def queryBookInfo(self, requestUrl):
        '''
        单本书归档
        '''
        request = urllib.request.Request(requestUrl, headers=self.headers)
        response = urllib.request.urlopen(request)
        data = response.read().decode('gbk')
        soup = BeautifulSoup(data, 'lxml')

        name_tag = soup.select("#maininfo #info h1")[0]
        cover_tag = soup.select(".box_con  #sidebar  #fmimg  img")[0]
        author_tag = soup.select("#maininfo #info p")[0]
        type_tag = soup.select(".con_top")[0]
        #words_tag =  soup.select(".book-info p em")[0]
        status_tag = soup.select("#info p")[2]
        summary_tag = soup.select("#maininfo #intro p")[0]
        #label_tags =  soup.select(".book-state .detail .tag-wrap .tags")
        #volumn_tags = soup.select('.catalog-content-wrap .volume-wrap h3')
        chapter_tags = soup.select(".box_con #list dd a")

        book = dict()
        pattern_id =  re.compile(r'[\s\/]+')

        book['tags'] = ''
        book['xbookId'] =  re.split(pattern_id, requestUrl)[2]
        book['bookName'] = name_tag.text
        book['cover'] = "http://www.biquge.com.tw%s" % (cover_tag.attrs['src'].strip())
        book['author'] = author_tag.text.split('：')[1]
        book['bookTypeId'] = self.convertToQidianType(type_tag.text)
        book['wordNumbers'] = 0
        book["lastupdate"] = status_tag.text.split('：')[1]

        t1 = time.strptime(book["lastupdate"], "%Y-%m-%d")
        y1,m1,d1 = t1[0:3]
        timeSpan = (datetime.datetime.now()-datetime.datetime(y1,m1,d1)).days
        if timeSpan < 7:
            book['status'] = 0
        else:
            book['status'] = 1

        book['summary'] = summary_tag.text.strip()

        request_url_list = []
        chapters = []
        count = len(chapter_tags)
        for i in  range(0, count):
            chapter_tag = chapter_tags[i]

            chapter = dict()
            request_url = "http://www.biquge.com.tw%s" % chapter_tag.attrs['href']

            chapter['chapterName'] = chapter_tag.text
            chapter['wordNumbers'] = 0
            chapter['updatetime'] = '1999-01-01'
            chapter['free'] = 1
            chapter['sort'] = i + 1
            chapter['xchapterId'] = re.split(pattern_id, request_url)[-1].split('.')[0]
            chapter['xbookId'] = book['xbookId']

            chapters.append(chapter)
            #content_key = "%s|content|%s|%s" % (self.siteId, book['xbookId'], chapter['xchapterId'])
            #if self.mRedis.isValidKey(content_key):
                #continue
            request_url_list.append(request_url)
        self.mRedis.setChapters(chapters)
        self.mRedis.addRequests(request_url_list)
        self.mRedis.setBookHash(book)
        return book

    def queryContent(self, requestUrl):
        """
        章节详情
        """
        content = dict()
        request = urllib.request.Request(requestUrl, headers=self.headers)
        response = urllib.request.urlopen(request)
        data = response.read().decode('gbk')
        soup = BeautifulSoup(data, 'lxml')

        pattern =  re.compile(r'[\s\/]+')
        pattern_book_href = re.compile(r'[\s\#]+')
        exclude_str = ",.:[]|!@#$%^&*()""，。！？、（）【】<>《》=：+-*—“”…"

        book_id_tag = soup.select('.box_con .con_top  a')[1]
        text_tags = soup.select('.box_con #content')[0].contents
        text_array = []
        for text_tag in text_tags:
            text_array.append(str(text_tag).strip())
        texts = ''.join(text_array)
        nonbreakspace = u'\xa0'
        texts = texts.replace(nonbreakspace, '&#8194;')
        texts = texts.replace('"', '&quot;')
        texts = texts.replace("'", "&apos;")
        wordNum = 0
        for char in texts:
            if char.strip() == None:
                continue
            if char.strip() not in exclude_str:
                wordNum += 1

        book_href = re.split(pattern_book_href, book_id_tag.attrs['href'])[0]

        content["wordNumbers"] = wordNum
        content['xchapterId'] = re.split(pattern, requestUrl)[3].split('.')[0]
        content["xbookId"] = re.split(pattern, book_href)[2]
        content['text'] = texts

        self.mRedis.setContentHash(content)

        return content


    def convertToQidianType(self, bookType):
        typeMap = {'玄幻' : '玄幻小说', '仙侠' : '修真小说', '都市':'都市小说', '历史':'历史小说', 
        '游戏':'网游小说', '科幻':'科幻小说', '灵异':'恐怖小说'}
        res = '未知'
        for key in typeMap:
            if typeMap[key] in bookType:
                res = key
        return res

    def addError(self, requestUrl):
        self.mRedis.addSpiderError(requestUrl)

