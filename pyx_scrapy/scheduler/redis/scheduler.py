# -*- coding: utf-8 -*-

# 自定义Scheduler

import importlib
import logging
import time

import six
from pyx_scrapy.utils import get_redis_cli
from scrapy.utils.misc import load_object

logger = logging.getLogger(__name__)


class Scheduler(object):
    '''
    自定义Scheduler类，使用redis保存队列数据以及去重
    '''
    # 要删除的meta中的key
    remove_meta_keys = ['depth']

    def __init__(self, server,
                 persist=True,
                 flush_on_start=False,
                 queue_key='%(spider)sRequests',
                 queue_cls='.queue.SpiderQueue',
                 dupefilter_key='%(spider)sDupefilter',
                 dupefilter_cls='.dupefilter.RFPDupeFilter',
                 idle_before_close=0,
                 serializer=None,
                 request_reqser=None):
        '''
        初始化Scheduler
        :param server: redis链接
        :param persist: 是否持久化，若为false，则spider关闭时会清空队列
        :param flush_on_start: 在启动spider时是否清空队列
        :param queue_key: 队列rediskey
        :param queue_cls: 队列类名
        :param dupefilter_key: 过滤rediskey
        :param dupefilter_cls: 过滤器类名
        :param idle_before_close: redis pop时的超时时间
        :param serializer: 序列化类
        '''
        if idle_before_close < 0:
            raise TypeError("idle_before_close cannot be negative")

        self.server = server
        self.persist = persist
        self.flush_on_start = flush_on_start
        self.queue_key = queue_key
        self.queue_cls = queue_cls
        self.dupefilter_cls = dupefilter_cls
        self.dupefilter_key = dupefilter_key
        self.idle_before_close = idle_before_close
        self.serializer = serializer
        self.request_reqser = request_reqser
        self.stats = None

    @classmethod
    def from_crawler(cls, crawler):
        if hasattr(cls, 'instance'):
            return cls.instance
        settings = crawler.settings

        kwargs = {
            'persist': settings.getbool('SCHEDULER_PERSIST', True),
            'flush_on_start': settings.getbool('SCHEDULER_FLUSH_ON_START', False),
            'idle_before_close': settings.getint('SCHEDULER_IDLE_BEFORE_CLOSE'),
        }

        optional = {
            'queue_key': 'SCHEDULER_QUEUE_KEY',
            'queue_cls': 'SCHEDULER_QUEUE_CLASS',
            'dupefilter_key': 'SCHEDULER_DUPEFILTER_KEY',
            'dupefilter_cls': 'DUPEFILTER_CLASS',
            'serializer': 'SCHEDULER_SERIALIZER',
            'request_reqser': 'SCHEDULER_REQUEST_REQSER'
        }
        for name, setting_name in optional.items():
            val = settings.get(setting_name)
            if val:
                kwargs[name] = val

        if isinstance(kwargs.get('serializer'), six.string_types):
            kwargs['serializer'] = importlib.import_module(kwargs['serializer'])
        if isinstance(kwargs.get('request_reqser'), six.string_types):
            kwargs['request_reqser'] = importlib.import_module(kwargs['request_reqser'])

        redis_config = settings.getdict('REDIS_CONFIG', {})
        server = get_redis_cli(**redis_config)
        # 检查服务器是否联通
        # server.ping()

        instance = cls(server, **kwargs)
        instance.stats = crawler.stats
        instance.close_if_idle = settings.getbool('CLOSE_IF_IDLE', True),
        cls.max_idle_time = settings.getfloat('MAX_IDLE_TIME', 0)
        cls.last_idle_time = 0
        cls.instance = instance
        return instance

    def open(self, spider):
        self.spider = spider
        if hasattr(spider, 'close_if_idle'):
            self.close_if_idle = spider.close_if_idle

        try:
            self.queue = load_object(self.queue_cls)(
                server=self.server,
                spider=spider,
                key=self.queue_key % {'spider': spider.name},
                serializer=self.serializer,
                request_reqser=self.request_reqser
            )
        except TypeError as e:
            raise ValueError("Failed to instantiate queue class '%s': %s",
                             self.queue_cls, e)

        try:
            # from krscrapy.scheduler.es.dupefilter import ESRFPDupeFilter
            from pyx_scrapy.scheduler.ssdb import SSDBDupeFilter
            from scrapy.utils.project import get_project_settings

            if load_object(self.dupefilter_cls) == SSDBDupeFilter:
                setting = get_project_settings()
                self.df = SSDBDupeFilter.from_settings(setting)
            else:
                self.df = load_object(self.dupefilter_cls)(
                    server=self.server,
                    key=self.dupefilter_key % {'spider': spider.name},
                    debug=spider.settings.getbool('DUPEFILTER_DEBUG'),
                )
        except TypeError as e:
            raise ValueError("Failed to instantiate dupefilter class '%s': %s",
                             self.dupefilter_cls, e)

        if self.flush_on_start:
            self.df.clear()
            self.queue.clear()
        # notice if there are requests already in the queue to resume the crawl
        if len(self.queue):
            spider.log("Resuming crawl (%d requests scheduled)" % len(self.queue))

    def close(self, reason):
        self.flush()

    def flush(self):
        if not self.persist:
            self.df.clear()
            self.queue.clear()

    def enqueue_request(self, request):
        '''
        入队列时调用
        :param request:
        :return:
        '''
        key = None
        if 'spider_name' in request.meta:
            key = self.dupefilter_key % {'spider': request.meta['spider_name']}
        if not request.dont_filter and self.df.request_seen(request, key):
            self.df.log(request, self.spider)
            return False
        # 入队各个地方都可能导入队列，没有参考意义，且问题{不是统计爬虫产生了多少种子，而是产生了的各类型分别的种子数量}
        # if self.stats:
        #     self.stats.inc_value('scheduler/enqueued/redis', spider=self.spider)

        key = None
        if 'spider_name' in request.meta:
            key = self.queue_key % {'spider': request.meta['spider_name']}
            del request.meta['spider_name']
        for k in self.remove_meta_keys:
            if k in request.meta:
                del request.meta[k]
        self.queue.push(request, key)
        return True

    def next_request(self):
        '''
        出队列时调用
        :return:
        '''
        block_pop_timeout = self.idle_before_close
        request = self.queue.pop(block_pop_timeout)
        if request and self.stats:
            self.stats.inc_value('scheduler/dequeued/redis', spider=self.spider)
        return request

    def __len__(self):
        '''
        返回队列长度
        :return:
        '''
        return len(self.queue)

    # def has_pending_requests(self):
    #     if self.close_if_idle and len(self) == 0:
    #         return False
    #     if len(self) == 0:
    #         self.spider.log('requests queue size is 0')
    #     return True
    def has_pending_requests(self):
        queue_length = len(self)
        if queue_length == 0:
            self.spider.log('requests queue size is 0')
        if self.close_if_idle and queue_length == 0:
            return False
        if self.max_idle_time:
            # 队列不为空清空时间
            if queue_length != 0:
                self.last_idle_time = 0
            # 队列首次为空的时间
            if queue_length == 0 and not self.last_idle_time:
                self.last_idle_time = time.time()
            if time.time() - self.last_idle_time > self.max_idle_time:
                self.spider.log('requests queue size is 0 and over max idle time close spider')
                return False
        return True
