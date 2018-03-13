"""
操作Aliyun OSS
"""
# -*- coding: utf-8 -*-
import oss2
import requests
from config import Config
from ..data.base import Book as BookModel
from ..data.base import db_session
from sqlalchemy import or_, and_

auth = oss2.Auth(Config.OSS_KEY_ID, Config.OSS_KEY_SECRET)

bucket = oss2.Bucket(auth, Config.END_POINT, Config.BUCKET_NAME, enable_crc=False)

class OSS:
    """
    oss操作类
    """
    def __init__(self):
        self.session = db_session
    def upload_image(self, book_id, url_img, img_type='cover'):
        """
        上传图片
        """
        res_url = ''
        if 'qidian_common' in url_img:
            img_type = 'banner'
        key = "img_%s_%s" % (img_type, book_id)
        res_url =  "%s%s" % (Config.HOST, key)
        try:
            exist = bucket.object_exists(key)
            if exist:
                return res_url
            else:
                input = requests.get(url_img)
                result = bucket.put_object(key, input, headers={'Content-Type': 'image/jpeg'})
                if result.status != 200:
                    res_url =  ''
        except Exception as e:
            res_url = ''
            print(e)
        finally:
            return res_url

    def upload_all_image(self):
        '''
        将外链存档OSS
        '''
        # pylint: disable=no-member  
        book_list = self.session.query(BookModel).filter(or_(~BookModel.banner.like('https://congjinruo%'), ~BookModel.cover.like('https://congjinruo%'))).all()
        for book in book_list:
            if book.banner is not None:
                book.banner = self.upload_image(book.xbook_id, book.banner)
            if book.cover is not None:
                book.cover = self.upload_image(book.xbook_id, book.cover)
            self.session.commit()
        self.session.close()

    def upload_file_by_url(self, key, url_img):
        '''
        根据url上传文件
        '''
        try:
            exist = bucket.object_exists(key)
            if exist:
                return True
            else:
                input = requests.get(url_img)
                result = bucket.put_object(key, input, headers={'Content-Type': 'image/jpeg'})
                if result.status != 200:
                    return False
                return True
        except Exception as e:
            print(e)
            return False

    def delete_object(self, my_prefix='2017'):
        """
        删除无用的文件
        """
        wait_delete_keys = []
        i = 0
        for obj in oss2.ObjectIterator(bucket, prefix=my_prefix):
            i += 1
            #最多允许一次性删除一千
            if i > 800:
                continue
            wait_delete_keys.append(obj.key)
        result = bucket.batch_delete_objects(wait_delete_keys)
        print('\n'.join(result.deleted_keys))
