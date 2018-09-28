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

# 用于爬取的调度器
SCHEDULER = 'pyx_scrapy.scheduler.scheduler_wrapper.Scheduler'
# 调度器队列
SCHEDULER_QUEUE_CLASS = {
    'pyx_scrapy.scheduler.redis.queue.SpiderPriorityQueue': (-5, 'inf'),
}
# 用于检测过滤重复请求的类
DUPEFILTER_CLASS = 'pyx_scrapy.scheduler.redis.dupefilter.RFPDupeFilter'

CONCURRENT_REQUESTS = 16

DOWNLOADER_MIDDLEWARES = {
    # 'pyx_scrapy.downloadermiddlewares.tencent_addkey.AddKeyMiddleware': 10,
    'pyx_scrapy.downloadermiddlewares.tencent_addkey_client.AddKeyClientMiddleware': 10,

}

ITEM_PIPELINES = {
}

REDIRECT_ENABLED = True

LOG_LEVEL = 'DEBUG'

SAVE_FILE_PATH = "D:\\test"

CLOSE_IF_IDLE = True
