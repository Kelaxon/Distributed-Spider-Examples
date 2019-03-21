import scrapy

from spiders.items import ProductIndexItem
from spiders.models import db_connect, get_session, ProductIndexModel
from spiders.spiders.miliashopIndexSpider import miliashopIndexSpider
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import exists
import xml.etree.ElementTree as ET


def get_newly_added_index(SITE_MAP):
    tree = ET.parse(SITE_MAP)
    root = tree.getroot()
    sitemap_list = []
    for atype in root.findall('{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
        url = atype.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text
        if(url.endswith('.html')):
            sitemap_list.append(url)


    engine = db_connect()
    session = get_session(engine)
    try:
        spider_list = [ans.product_url for ans in session.query(ProductIndexModel.product_url).all()]
        xor_list = list(set(sitemap_list).symmetric_difference(spider_list))
        ans_list = []
        for url in xor_list:
            if(not session.query(exists().where(ProductIndexModel.product_url == url)).scalar()):
                ans_list.append(url)

        print('database urls:', len(spider_list), 'sitemap urls:', len(sitemap_list), 'results:', len(ans_list))
        return ans_list

    except IntegrityError as e:
        print(e)
    finally:
        session.close()
        engine.dispose()

class miliashopIndexAddSpider(scrapy.Spider):
    SITE_MAP = '../../download/1_en_0_sitemap.xml'

    name = 'miliashopIndexAddSpider'
    custom_settings = miliashopIndexSpider.custom_settings
    custom_settings['LOG_FILE'] = '../../miliashopIndexAddSpider_log.txt'
    custom_settings['JOBDIR'] = '../../job  /miliashopIndexAddSpider'
    allowed_domains = miliashopIndexSpider.allowed_domains
    start_urls = None

    def __init__(self, *a, **kw):
        super(miliashopIndexAddSpider, self).__init__(*a, **kw)
        self.start_urls = get_newly_added_index(self.SITE_MAP)

    def parse(self, response):
        product_index = ProductIndexItem()
        product_index[ProductIndexItem.URL] = response.url
        product_index[ProductIndexItem.CATERGORY] = response.xpath("//span[@itemscope][1]//text()").extract_first()
        product_index[ProductIndexItem.NAME] = response.xpath("//h1/text()").extract_first()
        yield product_index


