"""
An scrapy spider
"""
from urllib.parse import urlencode

import scrapy
from spiders.items import ProductIndexItem


class itacasaCatalogSpider(scrapy.Spider):
    name = 'itacasaCatalogSpider'  # redis database name
    redis_key = 'itacasa:start_urls'

    custom_settings = {
        'ITEM_PIPELINES': {
            'spiders.pipelines.SaveMySQLPipeLine': 500,
        },
        'LOG_LEVEL': 'DEBUG',
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Host': 'www.itacasa.com',
            'Upgrade-Insecure-Requests': '1'
        }
    }

    total_page = 296
    cur_page = 0

    def start_requests(self):
        yield scrapy.Request(self.get_next_page_url(), dont_filter=True)

    def parse(self, response):
        product_names = response.xpath("//a[@class='m-product-name']//text()").extract()
        product_urls = response.xpath("//a[@class='m-product-name']//@href").extract()
        for i in range(len(product_names)):
            product_index = ProductIndexItem()
            product_index[ProductIndexItem.NAME] = product_names[i]
            product_index[ProductIndexItem.URL] = product_urls[i]
            product_index[ProductIndexItem.CATERGORY] = None
            yield product_index

        # crawl next page
        next_page_url = self.get_next_page_url()
        if(next_page_url):
            yield scrapy.Request(next_page_url, dont_filter=True, callback=self.parse)

    def get_next_page_url(self):
        if self.cur_page <= self.total_page:
            self.cur_page += 1
            url = 'http://www.itacasa.com/mall/product'
            params = {
                'index': self.cur_page,
                'size': 60,
                'sort': 'LATEST_DESC'
            }
            url = url + '/?' + urlencode(params)
            return url
