# -*- coding: utf-8 -*-

import json
import os

from pydispatch import dispatcher
from qiniu import put_file, Auth
from scrapy import signals
from sqlalchemy.exc import IntegrityError, StatementError, OperationalError
import logging
import scrapy
from scrapy.pipelines.images import ImagesPipeline
from slugify import slugify
from spiders.items import ProductIndexItem, ProductItem, Color
from spiders.models import indexItem2model, productItem2model, db_connect, get_session, ProductIndexModel


class ProductImagesPipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        images = [x for ok, x in results if ok]
        item['images'] = images
        return item

class MySQLPipeLine(object):

    def __init__(self):
        dispatcher.connect(self.spider_closed, signals.spider_closed)
        self.engine = db_connect()
        self.session = get_session(self.engine)

    # close db connection
    def spider_closed(self, spider, reason):
        self.session.close()
        self.engine.dispose()


class ItacasaMySQLPipeLine(MySQLPipeLine):

    def process_item(self, item, spider):
        # base on url, get product_index
        for i in range(3):
            try:
                product_index = self.sess.query(ProductIndexModel).filter(
                    ProductIndexModel.product_url == item.get(ProductItem.URL)).scalar()
                product = productItem2model(item)
                product_index.product = product
                self.sess.commit()
                break
            except (IntegrityError, OperationalError, StatementError) as e:
                self.sess.rollback()
                spider.log((item, e), logging.ERROR)
        return item


class SaveProductMySQLPipeLine(object):

    def __init__(self):
        self.engine = db_connect()
        self.sess = get_session(self.engine)

    def process_item(self, item, spider):
        # base on url, get product_index
        for i in range(3):
            try:
                product_index = self.sess.query(ProductIndexModel).filter(
                    ProductIndexModel.product_url == item.get(ProductItem.URL)).scalar()
                product = productItem2model(item)
                product_index.product = product
                self.sess.commit()
                break
            except (IntegrityError, OperationalError, StatementError) as e:
                self.sess.rollback()
                spider.log((item, e), logging.ERROR)
        return item


class QiniuUploader:
    def __init__(self, settings=None):
        self.access_key = settings.get('PIPELINE_QINIU_AK')
        self.secret_key = settings.get('PIPELINE_QINIU_SK')
        self.bucket = settings.get('PIPELINE_QINIU_BUCKET')
        self.q = Auth(self.access_key, self.secret_key)
        self.expires = settings.getint('FILES_EXPIRES')
        self.storage_path = settings.get('IMAGES_STORE')

    def _get_upload_token(self, key):
        return self.q.upload_token(self.bucket, key, 3600)

    def upload_img(self, local_img_path, key):
        '''
        using short img_path as the file key in Qiniu bucket
        put_file(token, key, localfile)
        '''
        ret, info = put_file(self._get_upload_token(key), key, local_img_path)
        return ret, info


class ProductAllImagesPipeline(ImagesPipeline):

    @classmethod
    def from_settings(cls, settings):
        return cls(
            settings=settings
        )

    def __init__(self, settings=None):
        super(ProductAllImagesPipeline, self).__init__(store_uri=settings['IMAGES_STORE'], settings=settings)
        self.store_uri = settings['IMAGES_STORE']
        self.qiniu_uploader = QiniuUploader(settings)

    def extract_color_img_download_url(self, item):
        for attribute in item.get('attributes', []):
            for color in attribute.get('colors', []):
                yield color['image_url']

    def extract_product_img_download_url(self, item):
        for img_url in item.get('image_urls', []):
            yield img_url

    def get_media_requests(self, item, info):
        # download color imgs
        for index, img_url in enumerate(item.get('image_urls', [])):
            img_name = 'img_pd/' + slugify(
                item.get(ProductItem.NAME) + ' ' + str(index + 1)) + os.path.splitext(img_url)[
                           -1]  # generate product img name
            yield scrapy.Request(img_url, meta={'img_name': img_name})

        # download color imgs
        for attribute in item.get('attributes', []):
            for index, color in enumerate(attribute.get('colors', [])):
                img_name = 'img_co/' + slugify(
                    color.get(Color.COLOR_NAME)) + os.path.splitext(img_url)[-1]
                # generate color img name
                yield scrapy.Request(color.get('image_url'), meta={'img_name': img_name})

    def file_path(self, request, response=None, info=None):
        '''
        Here defines image storage path
        '''
        return request.meta.get('img_name')

    def item_completed(self, results, item, info):
        '''
        This method is the callback of after downloading images.
        First distinct 2 type of image results according to 'path'.
        images contain: url(download url), path(local storage path), checksum
        When images are downloaded and saved in local storage, call QiniuUploader to upload local images
        '''
        images = [x for ok, x in results if ok]

        # distinct 2 type of images
        product_img_paths = []
        color_img_paths = []
        for image in images:
            if image.get('path').startswith('img_pd'):
                product_img_paths.append(image.get('path'))
            else:
                color_img_paths.append(image.get('path'))

        # set item fields
        item['images'] = product_img_paths
        cur = 0
        for i in range(len(item.get('attributes', []))):  # for each attribute
            for j in range(len(item.get('attributes')[i].get('colors', []))):
                if color_img_paths:
                    item.get('attributes')[i].get('colors')[j]['image'] = color_img_paths[cur]
                    cur += 1

        # Due to multiple processes running in local, upload and remove repeating color img may cause conflict
        # Even so the spider is usable, because Qiniu server provides duplicate storage,
        if (images):
            for image in images:
                img_location = os.path.join(self.store_uri, image.get('path'))
                if (os.path.isfile(img_location)):
                    ret, info = self.qiniu_uploader.upload_img(img_location, key=image.get('path'))
                # else:
                #     logging.log(logging.ERROR, 'image: {} does not exist'.format(img_location))

                # after uploading successfully, delete local file
                if ret:
                    if (os.path.isfile(img_location)):
                        os.remove(img_location)
                    # else:
                    #     logging.log(logging.ERROR, 'after uploading, image: {} does not exist'.format(img_location))
                else:
                    logging.log(logging.ERROR, '{} cannot upload, due to: {}'.format(image.get('path'), info))
        return item


class SaveMySQLPipeLine(object):
    def __init__(self):
        self.engine = db_connect()
        self.sess = get_session(self.engine)
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def process_item(self, item, spider):
        model = None
        if (isinstance(item, ProductIndexItem)):
            model = indexItem2model(item)
        elif (isinstance(item, ProductItem)):
            model = productItem2model(item)
        try:
            self.sess.add(model)
            self.sess.commit()
        except IntegrityError as e:
            self.sess.rollback()
            if (isinstance(item, ProductIndexItem)):
                spider.log((item, e), logging.ERROR)
        return item

    def spider_closed(self, spider):
        self.sess.close()
        self.engine.dispose()


class JsonWriterPipeline(object):
    def process_item(self, item, spider):
        file_name = '../../download/{}.json'.format(item['product_name'])
        file = open(file_name, 'w')
        line = json.dumps(dict(item)) + "\n"
        file.write(line)
        file.close()
        return item
