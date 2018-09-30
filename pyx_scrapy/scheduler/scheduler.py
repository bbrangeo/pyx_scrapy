# coding:utf-8


import importlib
import logging

import six
from scrapy.utils.misc import load_object

from . import SchedulerDefaultConfs

logger = logging.getLogger(__name__)


class SScheduler(object):
    """
    redis scheduler
    """

    def __init__(self, settings,
                 queue_cls=SchedulerDefaultConfs.QUEUE_CLS,
                 queue_key=SchedulerDefaultConfs.QUEUE_KEY,
                 serializer=None,
                 request_reqser=None):
        self.settings = settings

        self.queue_cls = queue_cls
        self.queue_key = queue_key

        self.serializer = serializer
        self.request_reqser = request_reqser

    @classmethod
    def from_crawler(cls, crawler):

        """
        单例实现，同一个CrawlerProcess运行多爬虫有问题  => crawler 唯一关联 engine

        scrapy框架现状，一个crawler一个engine {engine内部是独立的scheduler,downloader,itempipeline}
        """
        # if hasattr(cls, 'instance'):
        #     return cls.instance
        settings = crawler.settings

        queue_cls = settings.get('SCHEDULER_QUEUE_CLASS', SchedulerDefaultConfs.QUEUE_CLS)
        queue_key = settings.get('SCHEDULER_QUEUE_KEY', SchedulerDefaultConfs.QUEUE_KEY)

        serializer = settings.get('SCHEDULER_SERIALIZER', None)
        request_reqser = settings.get('SCHEDULER_REQUEST_REQSER', None)
        if isinstance(serializer, six.string_types):
            serializer = importlib.import_module(serializer)
        if isinstance(request_reqser, six.string_types):
            request_reqser = importlib.import_module(request_reqser)

        cls_object = cls(settings,
                         queue_cls=queue_cls,
                         queue_key=queue_key,
                         serializer=serializer,
                         request_reqser=request_reqser)

        cls_object.stats = crawler.stats

        cls_object.close_if_idle = settings.getbool('CLOSE_IF_IDLE', True)

        # cls.instance = cls_object
        return cls_object

    def open(self, spider):
        self.spider = spider

        if hasattr(spider, "close_if_idle"):
            self.close_if_idle = spider.close_if_idle

        # 初始化队列
        try:
            self.queue = load_object(self.queue_cls).from_settings(
                self.settings,
                spider=spider,
                key=self.queue_key % {'spider': spider.name},
                serializer=self.serializer,
                request_reqser=self.request_reqser)
        except TypeError as e:
            raise ValueError("Failed to instantiate queue class '%s': %s",
                             self.queue_cls, e)

    def close(self, reason):
        logger.info('scheduler close method call %s', reason)

    def enqueue_request(self, request):
        # stats
        if self.stats:
            self.stats.inc_value('scheduler/enqueued/redis', spider=self.spider)

        # enqueue
        if 'spider_name' in request.meta:
            key = self.queue_key % {'spider': request.meta['spider_name']}
            del request.meta['spider_name']

        self.queue.push(request, key)
        return True

    def next_request(self):
        request = self.queue.pop()
        if request and self.stats:
            self.stats.inc_value('scheduler/dequeued/redis', spider=self.spider)
        return request

    def __len__(self):
        return len(self.queue)

    def has_pending_requests(self):
        if self.close_if_idle and len(self) == 0:
            logger.info("This spider is closing : %s ", self.spider.name)
            return False
        return True