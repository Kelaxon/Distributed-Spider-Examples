from spiders.fix import toPlainText, fixDeco
from spiders.items import *
from scrapy.http import Request
from scrapy.selector import Selector
from urllib.parse import urlencode
import json



class miliashopIndexSpider(scrapy.Spider):
    name = 'miliashopIndexSpider'
    custom_settings = {
        'ITEM_PIPELINES': {
            # 'spiders.pipelines.JsonWriterPipeline': 1,
            'scrapy_qiniu.QiniuPipeline': 1,
            'spiders.pipelines.SaveMySQLPipeLine': 10,
            'spiders.pipelines.MiliashopSpiderPipeline': None,
        },
        'LOG_FILE': '../../miliashopIndexSpider_log.txt',
        'JOBDIR':'../../job/miliashopIndexSpider',
        'LOG_LEVEL' : 'ERROR',

    }
    allowed_domains = ['miliashop.com']

    url = 'https://www.miliashop.com/modules/blocklayered/blocklayered-ajax.php'
    params = {'id_category_layered': 51, 'p': 1}

    # 51-furniture
    # 30-outdoor
    # 55-office
    # 53-lighting
    # 142-kitchen
    # 166-in-stock
    # 173-ready-for-shipping
    # 174-rock-furniture
    # 175-futuristic-furniture
    # 176-contemporary-furniture
    # 177-sustainable-furniture
    # 178-artist
    # 186-art
    # 189-bathroom
    # 199-sale-s-kartell
    # 288-kitchens
    category_ids = [51, 30, 55, 53, 142, 166, 173, 174, 175, 176, 177, 178, 186, 189, 199, 288]
    cur_category = 0

    def start_requests(self):
        print('cur_category: ', self.cur_category)
        url = self.url + '/?' + urlencode(self.params)
        yield scrapy.Request(url, dont_filter=True)

    def parse(self, response):

        # get total page number
        html = self.response_to_json(response, 'pagination_bottom')
        tmp_list = Selector(text=html).xpath("//span/text()").extract()
        page_number = int(tmp_list[-1]) if tmp_list else 0

        # parse each page
        for i in range(1, page_number + 1):
            print('page:', i)
            if (i == 1):
                for item in self.parse_page(response):
                    yield item
            else:
                yield Request(self.get_page_url(i), meta={'category': self.cur_category+1, 'page': i},
                              callback=self.parse_page, dont_filter=True)

        # next category
        self.cur_category += 1
        if self.cur_category < len(self.category_ids):  # if has next category
            print('category url', self.get_page_url(1))
            yield Request(self.get_page_url(1), callback=self.parse, dont_filter=True)

    def response_to_json(self, response, key):
        return json.loads(response.body_as_unicode()).get(key)

    def get_page_url(self, param_p):
        params = {'id_category_layered': self.category_ids[self.cur_category], 'p': param_p}
        return self.url + '/?' + urlencode(params)

    def parse_page(self, response):
        # debug
        # print('category: ', response.meta.get('category'), 'page: ',response.meta.get('page'))

        html = json.loads(response.body_as_unicode())
        selector = Selector(text=html['productList'])
        urls = selector.xpath("//a[@class='product_img_link']//@href").extract()
        category = html['heading']
        product_name = [fixDeco(toPlainText(x.encode('latin1').decode('utf-8'))) for x in
                        selector.xpath("//a[@class='product-name']//@title").extract()]
        product_indexs = []
        for i in range(len(urls)):
            product_index = ProductIndexItem()
            product_index[ProductIndexItem.URL] = urls[i]
            product_index[ProductIndexItem.CATERGORY] = category
            product_index[ProductIndexItem.NAME] = product_name[i]
            product_indexs.append(product_index)
        return product_indexs


def getCategoryID(url):
    return url.split('/')[-1].split('-')[0]

