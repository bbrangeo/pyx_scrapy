# -*- coding: utf-8 -*-

BOT_NAME = 'pyx_scrapy'

SPIDER_MODULES = ['pyx_scrapy.spiders']

NEWSPIDER_MODULE = 'pyx_scrapy.spiders'

ROBOTSTXT_OBEY = False

SCHEDULER = 'pyx_scrapy.scheduler.scheduler.SScheduler'

SCHEDULER_QUEUE_CLASS = 'pyx_scrapy.scheduler.queue.SpiderShareQueue'

CONCURRENT_REQUESTS = 32

DOWNLOADER_MIDDLEWARES = {
    'pyx_scrapy.downloadermiddlewares.tencent_vkey.VKeyMp3Middleware': 10,
    'pyx_scrapy.downloadermiddlewares.tencent_vkey.VKeyFlacMiddleware': 10,
    'pyx_scrapy.downloadermiddlewares.useragent.RandomUserAgentMiddleware': 550,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'pyx_scrapy.downloadermiddlewares.headers.HeadersMiddleware': 2000,
    'pyx_scrapy.downloadermiddlewares.referer.RefererMiddleware': 2001,
    # 'pyx_scrapy.downloadermiddlewares.url.UrlMiddleware': 9999,
}

ITEM_PIPELINES = {
    'pyx_scrapy.pipelines.OutputCSVPipeline': 10
}

DOWNLOAD_TIMEOUT = 30

# 1024M
DOWNLOAD_MAXSIZE = 1073741824
# 32M
# DOWNLOAD_WARNSIZE = 33554432
DOWNLOAD_WARNSIZE = 134217728

REACTOR_THREADPOOL_MAXSIZE = 20

REDIRECT_ENABLED = True

LOG_LEVEL = 'INFO'

FILES_PATH = ".\\files"
