from scrapy_redis.spiders import RedisSpider
from spiders.fix import toPlainText, fixColorName, concateTextList
from spiders.items import *


class rd_miliashopSpider(RedisSpider):
    name = 'rd_miliashopSpider'  # redis database name
    redis_key = 'miliashop:start_urls'

    
    custom_settings = {
        'ITEM_PIPELINES': {
            'spiders.pipelines.ProductAllImagesPipeline':1,
            'spiders.pipelines.SaveProductMySQLPipeLine': 500,
        },
        'IMAGES_STORE': '../../download',
        'FILES_EXPIRES': 30,
        'LOG_LEVEL': 'INFO',
        # 'LOG_FILE': '../log/{}.log'.format(name),
    }

    allowed_domains = ['miliashop.com']
    start_urls = []

    def __init__(self, *a, **kw):
        super(rd_miliashopSpider, self).__init__(*a, **kw)

    def parse(self, response):
        yield self.parse_this_page(response)


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



def getLargeImageUrl(urls):
    return [url.replace('cart_default', 'large_default') for url in urls]
