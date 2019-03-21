from scrapy import signals, Request
from spiders.fix import toPlainText, fixColorName, concateTextList
from spiders.items import *
from spiders.models import db_connect, get_session, ProductIndexModel


class miliashopSpider(scrapy.Spider):
    name = 'miliashopSpider'
    custom_settings = {
        'ITEM_PIPELINES': {
            # 'spiders.pipelines.ProductImagesPipeline': 1,  # download
            # 'spiders.pipelines.ColorImagesPipeline': 2,  # download
            # 'spiders.pipelines.QiniuPipeline': 1,
            'spiders.pipelines.ProductAllImagesPipeline':1,
            'spiders.pipelines.SaveProductMySQLPipeLine': 500,
            'spiders.pipelines.MiliashopSpiderPipeline': None,
        },
        'IMAGES_STORE': '../../download',
        'FILES_EXPIRES': 30,
        'JOBDIR': '../../job/miliashopSpider',
        # 'LOG_FILE': '../../miliashopSpider_log.txt',
        'LOG_LEVEL': 'ERROR',
    }

    allowed_domains = ['miliashop.com']
    start_urls = []
    product_index = None
    engine = None
    session = None

    def __init__(self, *a, **kw):
        super(miliashopSpider, self).__init__(*a, **kw)
        self.engine = db_connect()
        self.session = get_session(self.engine)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(miliashopSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signals.spider_closed)
        return spider

    def get_next_product_index(self):
        return self.session.query(ProductIndexModel).filter(ProductIndexModel.product == None).first()  # cannot use is None

    def start_requests(self):
        product_index = self.get_next_product_index()
        if (product_index):
            print('start crawling: ', product_index.product_name)
            yield Request(product_index.product_url, dont_filter=True,
                          meta=dict(product_index_id=product_index.product_index_id))

    def parse(self, response):
        yield self.parse_this_page(response)

        # next product TODO
        # next_product_index = self.get_next_product_index()
        # if(next_product_index):
        #     yield Request(next_product_index.product_url, callback=self.parse, dont_filter=True, meta=dict(product_index_id=next_product_index.product_index_id))

    def parse_this_page(self, response):
        product = ProductItem()
        product['product_index_id'] = response.meta.get('product_index_id')
        product['name'] = response.xpath("//h1/text()").extract_first()
        product['price'] = response.xpath("//span[@id='our_price_display']/text()").extract_first()
        product['url'] = response.url
        product['image_urls'] = getLargeImageUrl(response.xpath("//img[@height='90']/@src").extract())
        product['short_description'] = toPlainText(
            response.xpath(
                "//div[@id='short_description_content']//*[not(self::strong)]/text()").extract_first())
        product['full_description'] = toPlainText(
            concateTextList(response.xpath("//div[@class='rte']/p[last()]/text()").extract()))

        product['category'] = response.xpath(
            "//span[@class='navigation_page']//text()[not(contains(., '>'))]").extract()[:-1]  # except the last one

        # Attributes
        attributes = []
        attribute_labels = response.xpath("//label[@class='attribute_label']/text()").extract()
        for index in range(len(attribute_labels)):
            attribute = Attribute()
            attribute['label'] = attribute_labels[index]

            # deal with each attribute
            attribute_type = \
                response.xpath("//fieldset[{}]/div[@class='attribute_list']/*[1]/@class".format(index + 1)).extract()[0]
            if attribute_type == 'trasparente':  # color type
                color_names = fixColorName(response.xpath(
                    "//fieldset[{}]/div[@class='attribute_list']//li/a/@title".format(index + 1)).extract())
                color_image_urls = response.xpath(
                    "//fieldset[{}]/div[@class='attribute_list']//li/a/img/@src".format(index + 1)).extract()

                colors = []
                for index in range(len(color_names)):
                    color = Color()
                    color['name'] = color_names[index]
                    color['image_url'] = color_image_urls[index]
                    colors.append(dict(color))

                attribute['colors'] = colors

            elif attribute_type == 'form-control attribute_select no-print':  # option type
                options = response.xpath(
                    "//fieldset[{}]/div[@class='attribute_list']/select//@title".format(index + 1)).extract()
                attribute['options'] = options

            attributes.append(dict(attribute))
        product['attributes'] = attributes

        # MoreInfo
        keys = [toPlainText(k) for k in response.xpath("//table[@class='table-data-sheet']//td[1]/text()").extract()]
        values = [toPlainText(v) for v in response.xpath("//table[@class='table-data-sheet']//td[2]/text()").extract()]
        product['more_info'] = dict(zip(keys, values))

        return product

    def spider_closed(self, spider):
        self.session.close()
        self.engine.dispose()


def getLargeImageUrl(urls):
    return [url.replace('cart_default', 'large_default') for url in urls]
