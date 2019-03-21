from scrapy import cmdline

name = '../spiders/itacasaCatalogSpider.py'
cmd = 'scrapy runspider {0}'.format(name)
cmdline.execute(cmd.split())
