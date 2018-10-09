# coding:utf-8


import importlib
import logging
import time

import six
from scrapy.utils.misc import load_object
from twisted.internet import task

from . import SchedulerDefaultConfs

logger = logging.getLogger(__name__)


class SScheduler(object):

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

        self.looping_call_interval = 5
        self.pause_time_interval = 30
        self.pop_request_none_times = 0

        self.idle_max_time = 60 * 3
        self.next_close_timestamp = -1

    @classmethod
    def from_crawler(cls, crawler):
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

        cls_object.crawler = crawler

        return cls_object

    def open(self, spider):
        self.spider = spider

        # 初始化队列
        try:
            self.queue = load_object(self.queue_cls).from_settings(
                self.settings,
                spider=spider,
                key=self.queue_key % {'spider': spider.name},
                serializer=self.serializer,
                request_reqser=self.request_reqser)
        except TypeError as e:
            raise ValueError("Failed to instantiate queue class '%s': %s", self.queue_cls, e)

    def close(self, reason):
        logger.info('scheduler close method call %s', reason)

    def enqueue_request(self, request):
        key = self.queue_key % {'spider': self.spider.name}
        if 'spider_name' in request.meta:
            key = self.queue_key % {'spider': request.meta['spider_name']}
            del request.meta['spider_name']

        self.queue.push(request, key)
        return True

    def next_request(self):
        request = self.queue.pop()
        if not request:
            self.pop_request_none_times += 1
            if self.pop_request_none_times > 10:
                logger.debug(" %s => scrapy engine stop " % self.spider.name)

                self.crawler.engine.pause()  # 暂停

                pause_timestamp = time.time()
                self.pause_engine_task = task.LoopingCall(self._pause_engine, pause_timestamp, self.pause_time_interval)
                self.pause_engine_task.start(self.looping_call_interval)
        else:
            self.pop_request_none_times = 0
            self.next_close_timestamp = time.time()

        return request

    def _pause_engine(self, pause_timestamp, interval):
        t = time.time() - pause_timestamp
        if t < interval:
            logger.debug(' %s => scrapy engine restart => %s seconds left' % (self.spider.name, int(interval - t + 1)))
        else:
            logger.debug(' %s => scrapy engine start' % self.spider.name)
            self.crawler.engine.unpause()
            self.pause_engine_task.stop()
            self.pop_request_none_times = 0

    def __len__(self):
        return len(self.queue)

    def has_pending_requests(self):
        if len(self) == 0:
            logger.info(" %s => queue is zero" % self.spider.name)
            idle_closeable = False if self.next_close_timestamp < 0 else (
                    time.time() - self.next_close_timestamp > self.idle_max_time
            )
            if idle_closeable:
                logger.info("The spider is closing : %s ", self.spider.name)
                return False
        return True
