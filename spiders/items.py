# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ProductIndexItem(scrapy.Item):
    KEY = 'product_name'
    NAME = 'product_name'
    URL = 'product_url'
    CATERGORY = 'product_parent_category'

    product_name = scrapy.Field()
    product_url = scrapy.Field()
    product_parent_category = scrapy.Field()

    def __repr__(self):
        return repr({self.NAME: self[self.NAME], self.URL: self[self.URL],
                     self.CATERGORY: self[self.CATERGORY]})


class ProductItem(scrapy.Item):
    KEY = 'name'
    NAME = 'name'
    URL = 'url'
    product_index_id = scrapy.Field()
    name = scrapy.Field()
    price = scrapy.Field()
    url = scrapy.Field()
    category = scrapy.Field()  # list
    image_urls = scrapy.Field()
    images = scrapy.Field()  # list
    short_description = scrapy.Field()
    full_description = scrapy.Field()

    # nest item
    attributes = scrapy.Field()  # list
    more_info = scrapy.Field()  # dict


class Attribute(scrapy.Item):
    label = scrapy.Field()
    colors = scrapy.Field()  # list
    options = scrapy.Field()  # list


class Color(scrapy.Item):
    COLOR_NAME = 'name'
    name = scrapy.Field()
    image_url = scrapy.Field()  # single
    image = scrapy.Field()
