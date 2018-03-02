import urllib, time, datetime, json, base64, urllib.request, re
from urllib import parse
from bs4 import BeautifulSoup
from ..utils.operate_redis import MRedis
class QidianSpider:
    """
    专爬起点
    """
    def __init__(self):
        """
        siteId: data from
        """
        self.siteId = 1
        self.headers =  {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) \
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36'}
        self.mRedis = MRedis(self.siteId)

    def queryBannerList(self, requestUrl):
        book = dict()
        request = urllib.request.Request(requestUrl, headers=self.headers)
        response = urllib.request.urlopen(request)
        data = response.read().decode('utf8')
        soup = BeautifulSoup(data)
        li_tags = soup.select('.box-center .focus-rec-wrap  ul')[0].select('li')
        pattern = re.compile(r'[\s\/]+')
        for i in range(0, len(li_tags), 1):
            a_tag = li_tags[i].select('a')[0]
            img_tag = li_tags[i].select('img')[0]
            info_a_tag = li_tags[i].select('.info a')[0]
            #request_url
            request_url =  a_tag.attrs['href']
            #封推
            book['banner'] = 'https:' + img_tag.attrs['src']
            #源站点书id
            book['xbookId'] = re.split(pattern, request_url)[3]
            #书名
            book['bookName'] = info_a_tag.attrs['title']
            #请求url
            self.mRedis.setBookHash(book)
            self.mRedis.addRequest(request_url)
                
        return 'success'

    def queryBookInfo(self, requestUrl):
        """
        作品详情，包含章节目录
        """
        request = urllib.request.Request(requestUrl, headers=self.headers)
        response = urllib.request.urlopen(request)
        data = response.read().decode('utf8')
        soup = BeautifulSoup(data)
        
        name_tag = soup.select(".book-info h1 em")[0]
        cover_tag = soup.select(".book-information .book-img a img")[0]
        author_tag = soup.select(".book-info h1 span .writer")[0]
        type_tag = soup.select(".book-info .tag .red")[0]
        words_tag =  soup.select(".book-info p em")[0]
        status_tag = soup.select(".book-info .tag .blue")[0]
        summary_tag = soup.select(".book-info-detail .book-intro p")[0]
        label_tags =  soup.select(".book-state .detail .tag-wrap .tags")
        volumn_tags = soup.select('.catalog-content-wrap .volume-wrap h3')
        chapter_tags = soup.select(".catalog-content-wrap .volume-wrap .cf li a")

        book = dict()
        pattern_id =  re.compile(r'[\s\/]+')
        pattern_info = re.compile(r'[\：\章]')

        tags = []
        for label_tag in label_tags:
            tag = label_tag.text
            if '连续' in tag:
                tags.append(tag)
        book['tags'] = '|'.join(tags)
        book['xbookId'] =  re.split(pattern_id, requestUrl)[3]
        book['bookName'] = name_tag.text
        book['cover'] = "https:%s" % (cover_tag.attrs['src'].strip())
        book['author'] = author_tag.text
        book['bookTypeId'] = type_tag.text
        book['wordNumbers'] = words_tag.text
        book['status'] = 1 if status_tag.text == '连载' else 0
        book['summary'] = summary_tag.text.strip()
        
        #for volumn_tag in volumn_tags:
            #print(volumn_tag.contents[2].strip())
        count = len(chapter_tags)
        for i in  range(0, count):
            chapter_tag = chapter_tags[i]
            info = re.split(pattern_info, chapter_tag.attrs['title'], 3)

            chapter = dict()
            request_url = "https:%s" % chapter_tag.attrs['href']

            chapter['chapterName'] = chapter_tag.text
            chapter['wordNumbers'] = info[3]
            chapter['updatetime'] = info[1].strip()
            chapter['free'] = 1 if  'vip' in request_url  else 0
            chapter['sort'] = i + 1
            chapter['xchapterId'] = re.split(pattern_id, request_url)[4]
            chapter['xbookId'] = book['xbookId']
            if i == count -1 :
                book["lastupdate"] = chapter['updatetime']

            self.mRedis.setChapterHash(chapter)
            content_key = "%s_content_%s_%s" % (self.siteId, book['xbookId'], chapter['xchapterId'])
            if self.mRedis.isValidKey(content_key):
                continue
            self.mRedis.addRequest(request_url)

        self.mRedis.setBookHash(book)

        return 'success'

    def queryContent(self, requestUrl):
        """
        章节详情
        """
        content = dict()
        request = urllib.request.Request(requestUrl, headers=self.headers)
        response = urllib.request.urlopen(request)
        data = response.read().decode('utf8')
        soup = BeautifulSoup(data)

        pattern =  re.compile(r'[\s\/]+')
        pattern_book_href = re.compile(r'[\s\#]+')
        book_id_tag = soup.select('.chapter-control a')[1]
        word_numbers_tag = soup.select('.main-text-wrap .info .j_chapterWordCut')[0]
        text_tags = soup.select('.main-text-wrap .j_readContent')[0].contents
        text_array = []
        for text_tag in text_tags:
            text_array.append(str(text_tag).strip())
        texts = ''.join(text_array)

        book_href = re.split(pattern_book_href, book_id_tag.attrs['href'])[0]

        content["wordNumbers"] = word_numbers_tag.text
        content['xchapterId'] = re.split(pattern, requestUrl)[4]
        content["xbookId"] = re.split(pattern, book_href)[3]
        content['text'] = texts

        self.mRedis.setContentHash(content)

        return 'success'

    def addError(self, requestUrl):
        self.mRedis.addSpiderError(requestUrl)

        

