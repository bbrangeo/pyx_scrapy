# -*- coding: utf-8 -*-

BOT_NAME = 'pyx_scrapy'

SPIDER_MODULES = ['pyx_scrapy.spiders']

NEWSPIDER_MODULE = 'pyx_scrapy.spiders'

ROBOTSTXT_OBEY = False

SCHEDULER = 'pyx_scrapy.scheduler.scheduler.SScheduler'
SCHEDULER_QUEUE_CLASS = 'pyx_scrapy.scheduler.queue.SpiderShareQueue'

CONCURRENT_REQUESTS = 16

DOWNLOADER_MIDDLEWARES = {
    'pyx_scrapy.downloadermiddlewares.tencent_addkey.AddKeyMiddleware': 10,
    'pyx_scrapy.downloadermiddlewares.tencent_addkey_client.AddKeyClientMiddleware': 10,
    'pyx_scrapy.downloadermiddlewares.useragent.RandomUserAgentMiddleware': 550,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'pyx_scrapy.downloadermiddlewares.headers.HeadersMiddleware': 2000,
}

ITEM_PIPELINES = {
    'pyx_scrapy.pipelines.OutputCSVPipeline': 10
}

REDIRECT_ENABLED = True

LOG_LEVEL = 'INFO'

FILES_PATH = ".\\files"

CLOSE_IF_IDLE = True
