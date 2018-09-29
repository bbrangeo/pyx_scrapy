# -*- coding: utf-8 -*-

BOT_NAME = 'pyx_scrapy'

SPIDER_MODULES = ['pyx_scrapy.spiders']

NEWSPIDER_MODULE = 'pyx_scrapy.spiders'

ROBOTSTXT_OBEY = False

REDIS_CONFIG = {
    "host": "tk",
    "port": 6379,
    "decode_responses": True,
}

SCHEDULER = 'pyx_scrapy_exts.scheduler.redis.scheduler.RedisScheduler'
SCHEDULER_QUEUE_CLASS = 'pyx_scrapy_exts.scheduler.redis.queue.PriorityQueue'
DUPEFILTER_CLASS = 'pyx_scrapy_exts.scheduler.dupefilter.RedisDupeFilter'

CONCURRENT_REQUESTS = 16

DOWNLOADER_MIDDLEWARES = {
    # 'pyx_scrapy.downloadermiddlewares.tencent_addkey.AddKeyMiddleware': 10,
    'pyx_scrapy.downloadermiddlewares.tencent_addkey_client.AddKeyClientMiddleware': 10,
    'pyx_scrapy_exts.downloadermiddlewares.useragent.RandomUserAgentMiddleware': 550,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'pyx_scrapy_exts.downloadermiddlewares.headers.HeadersMiddleware': 2000,
}

ITEM_PIPELINES = {
    'pyx_scrapy.pipelines.OutputCSVPipeline': 10
}

REDIRECT_ENABLED = True

LOG_LEVEL = 'DEBUG'

FILES_PATH = ".\\files"

CLOSE_IF_IDLE = True
