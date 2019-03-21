import config

# Scrapy-redis settings
# necessary, duplicate
#DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
# necessary, scheduler
#SCHEDULER = "scrapy_redis.scheduler.Scheduler"
# necessary, allow spider to pause and restart
#SCHEDULER_PERSIST = True

# redis database
REDIS_URL = config.REDIS_URL
CONNECTION_STRING = config.CONNECTION_STRING


# Qinu
PIPELINE_QINIU_AK = config.PIPELINE_QINIU_AK
PIPELINE_QINIU_SK = config.PIPELINE_QINIU_SK
PIPELINE_QINIU_BUCKET = config.PIPELINE_QINIU_BUCKET
PIPELINE_QINIU_ENABLED = config.PIPELINE_QINIU_ENABLED

BOT_NAME = 'spiders'
SPIDER_MODULES = ['spiders']
NEWSPIDER_MODULE = 'spiders'

FEED_EXPORT_ENCODING = 'utf-8'
# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'spiders (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 0.25
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Host': 'www.miliashop.com',
    'Referer': 'https://www.miliashop.com/en/',
    'Upgrade-Insecure-Requests': '1',
}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'spiders.middlewares.MiliashopSpiderSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
}
RANDOM_UA_TYPE = 'random'
FAKEUSERAGENT_FALLBACK = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html


# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
