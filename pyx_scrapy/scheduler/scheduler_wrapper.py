# -*- coding: utf-8 -*-

# 自定义Scheduler

import importlib
import logging
from collections import OrderedDict

import six
from scrapy.utils.misc import load_object

logger = logging.getLogger(__name__)


class Scheduler(object):
    remove_meta_keys = ['depth']

    def __init__(self, server_config,
                 persist=True,
                 flush_on_start=False,
                 queue_key='%(spider)sRequests',
                 queue_cls_dic=None,
                 dupefilter_key='%(spider)sDupefilter',
                 dupefilter_cls='.dupefilter.RFPDupeFilter',
                 idle_before_close=0,
                 serializer=None,
                 request_reqser=None):
        """
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
        """
        if idle_before_close < 0:
            raise TypeError("idle_before_close cannot be negative")

        self.server_config = server_config
        self.persist = persist
        self.flush_on_start = flush_on_start
        self.queue_key = queue_key
        self.queue_cls_dic = queue_cls_dic or {'.queue.SpiderQueue': None}
        self.dupefilter_cls = dupefilter_cls
        self.dupefilter_key = dupefilter_key
        self.idle_before_close = idle_before_close
        self.serializer = serializer
        self.request_reqser = request_reqser
        self.stats = None

        self.init_range = ('-inf', 'inf')

    @classmethod
    def from_crawler(cls, crawler):
        if hasattr(cls, 'instance'):
            return cls.instance
        settings = crawler.settings

        queue_cls_dic = settings.get('SCHEDULER_QUEUE_CLASS', {})

        persist = settings.getbool('SCHEDULER_PERSIST', True)
        flush_on_start = settings.getbool('SCHEDULER_FLUSH_ON_START', False)
        idle_before_close = settings.getint('SCHEDULER_IDLE_BEFORE_CLOSE')
        queue_key = settings.get('SCHEDULER_QUEUE_KEY', '%(spider)sRequests')
        dupefilter_key = settings.get('SCHEDULER_DUPEFILTER_KEY', '%(spider)sDupefilter')
        dupefilter_cls = settings.get('DUPEFILTER_CLASS', '.dupefilter.RFPDupeFilter')
        serializer = settings.get('SCHEDULER_SERIALIZER')
        request_reqser = settings.get('SCHEDULER_REQUEST_REQSER')

        if isinstance(serializer, six.string_types):
            serializer = importlib.import_module(serializer)
        if isinstance(request_reqser, six.string_types):
            request_reqser = importlib.import_module(request_reqser)

        server_config = settings
        # server = get_redis_cli(**redis_config)
        # 检查服务器是否联通
        # server.ping()
        instance = cls(
            server_config,
            persist=persist,
            flush_on_start=flush_on_start,
            queue_key=queue_key,
            queue_cls_dic=queue_cls_dic,
            dupefilter_key=dupefilter_key,
            dupefilter_cls=dupefilter_cls,
            idle_before_close=idle_before_close,
            serializer=serializer,
            request_reqser=request_reqser
        )
        instance.stats = crawler.stats
        cls.instance = instance
        return instance

    def open(self, spider):
        self.spider = spider
        self.close_if_idle = False
        if hasattr(spider, 'close_if_idle'):
            self.close_if_idle = spider.close_if_idle

        queue = {}
        for queue_name in self.queue_cls_dic:
            try:
                queue_range = self.queue_cls_dic[queue_name] or self.init_range
                queue_range = tuple(map(float, queue_range))
                queue_cls = load_object(queue_name)(
                    settings=self.server_config,
                    spider=spider,
                    key=self.queue_key % {'spider': spider.name},
                    serializer=self.serializer,
                    request_reqser=self.request_reqser
                )
                queue[queue_cls] = queue_range
            except TypeError as e:
                raise ValueError("Failed to instantiate queue class '%s': %s", queue_name, e)

        # 根据queue的优先级排序
        self.queue = OrderedDict(sorted(queue.items(), key=lambda x: x[1], reverse=True))
        try:
            self.df = load_object(self.dupefilter_cls).from_settings(
                settings=self.server_config,
                key=self.dupefilter_key % {'spider': spider.name},
                debug=spider.settings.getbool('DUPEFILTER_DEBUG'),
            )
        except TypeError as e:
            raise ValueError("Failed to instantiate dupefilter class '%s': %s",
                             self.dupefilter_cls, e)

        if self.flush_on_start:
            self.df.clear()
            for queue_cls in self.queue:
                queue_cls.clear()
        # notice if there are requests already in the queue to resume the crawl
        for queue_cls in self.queue:
            if len(queue_cls):
                spider.log("Resuming crawl (%d requests scheduled)" % len(self.queue))

    def close(self, reason):
        self.flush()

    def flush(self):
        if not self.persist:
            self.df.clear()
            for queue_cls in self.queue:
                queue_cls.clear()

    def enqueue_request(self, request):
        """
        入队列时调用
        :param request:
        :return:
        """
        key = None
        spider_name = self.spider.name
        if 'spider_name' in request.meta:
            key = self.dupefilter_key % {'spider': request.meta['spider_name']}
            spider_name = request.meta.get('spider_name')
        if not request.dont_filter and self.df.request_seen(request, key):
            self.df.log(request, self.spider)
            return False
        if self.stats:
            # 入队各个地方都可能导入队列，没有参考意义，且问题{不是统计爬虫产生了多少种子，而是产生了的各类型分别的种子数量}
            # self.stats.inc_value('scheduler/enqueued/redis', spider=self.spider)
            # self.stats._add_process(json.dumps(request.meta.get('queue_item')),
            #                         self.__class__.__name__+':'+get_current_function_name(),
            #                         spider_name)
            pass

        key = None
        if 'spider_name' in request.meta:
            key = self.queue_key % {'spider': request.meta['spider_name']}
            del request.meta['spider_name']
        for k in self.remove_meta_keys:
            if k in request.meta:
                del request.meta[k]

        priority = request.priority
        for queue in self.queue:
            if self._check_range(self.queue[queue], priority):
                queue.push(request, key)
                return True
        return False

    def next_request(self):
        '''
        出队列时调用
        :return:
        '''

        for queue in self.queue:
            block_pop_timeout = self.idle_before_close
            request = queue.pop(block_pop_timeout)
            if request and self.stats:
                self.stats.inc_value('scheduler/dequeued/redis', spider=self.spider)
            if not request:
                logger.debug('%s has no request' % queue)
                continue
            else:
                return request
        return

    def __len__(self):
        """
        返回队列长度
        :return:
        """
        return 2

    def get_length(self):
        d = []
        for queue in self.queue:
            d.append((len(queue), queue))
        return d

    # def has_pending_requests(self):
    #     if self.close_if_idle and len(self) == 0:
    #         return False
    #     if len(self) == 0:
    #         self.spider.log('requests queue size is 0')
    #     return True
    def has_pending_requests(self):
        queue_length_list = self.get_length()
        for q in queue_length_list:
            if q[0] == 0:
                self.spider.log(' %s requests queue size is 0' % q[1])
        return True

    @staticmethod
    def _check_range(queue_range, pri):
        if queue_range[0] < pri < queue_range[1]:
            return True
        return False
