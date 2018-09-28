# -*- coding: utf-8 -*-

# 自定义队列

import json

from pyx_scrapy.scheduler.common import reqser
from pyx_scrapy.utils.connection import get_redis_cli


class Base(object):
    '''
    队列父类定义
    '''

    def __init__(self, settings, spider, key, serializer=None, request_reqser=None):
        '''
        初始化队列
        :param server: redis链接
        :param spider:
        :param key:
        :param serializer:
        '''
        if serializer is None:
            serializer = json
        if not hasattr(serializer, 'loads'):
            raise TypeError("serializer does not implement 'loads' function: %r"
                            % serializer)
        if not hasattr(serializer, 'dumps'):
            raise TypeError("serializer '%s' does not implement 'dumps' function: %r"
                            % serializer)

        if request_reqser is None:
            request_reqser = reqser
        if not hasattr(request_reqser, 'request_to_dict'):
            raise TypeError("request_reqser does not implement 'request_to_dict' function: %r"
                            % request_reqser)
        if not hasattr(request_reqser, 'request_from_dict'):
            raise TypeError("request_reqser '%s' does not implement 'request_from_dict' function: %r"
                            % request_reqser)

        self.server = get_redis_cli(**settings.getdict('REDIS_CONFIG', {}))
        self.spider = spider
        self.key = key % {'spider': spider.name}
        self.serializer = serializer
        self.request_reqser = request_reqser

    def _encode_request(self, request):
        """Encode a request object"""
        obj = self.request_reqser.request_to_dict(request, self.spider)
        return self.serializer.dumps(obj)

    def _decode_request(self, encoded_request):
        """Decode an request previously encoded"""
        if isinstance(encoded_request, bytes):
            obj = self.serializer.loads(encoded_request.decode())
        else:
            obj = self.serializer.loads(encoded_request)
        return self.request_reqser.request_from_dict(obj, self.spider)

    def __len__(self):
        """Return the length of the queue"""
        raise NotImplementedError

    def push(self, request, key=None):
        """Push a request"""
        raise NotImplementedError

    def pop(self, timeout=0):
        """Pop a request"""
        raise NotImplementedError

    def clear(self):
        """Clear queue/stack"""
        self.server.delete(self.key)


class SpiderQueue(Base):
    """Per-spider FIFO queue"""

    def __len__(self):
        """Return the length of the queue"""
        return self.server.llen(self.key)

    def push(self, request, key=None):
        if key is None:
            key = self.key
        """Push a request"""
        self.server.lpush(key, self._encode_request(request))

    def pop(self, timeout=0):
        """Pop a request"""
        if timeout > 0:
            data = self.server.brpop(self.key, timeout)
            if isinstance(data, tuple):
                data = data[1]
        else:
            data = self.server.rpop(self.key)
        if data:
            return self._decode_request(data)


class SpiderPriorityQueue(Base):
    """Per-spider priority queue abstraction using redis' sorted set"""

    def __len__(self):
        """Return the length of the queue"""
        return self.server.zcard(self.key)

    def push(self, request, key=None):
        if key is None:
            key = self.key
        """Push a request"""
        data = self._encode_request(request)
        score = -request.priority
        # We don't use zadd method as the order of arguments change depending on
        # whether the class is Redis or StrictRedis, and the option of using
        # kwargs only accepts strings, not bytes.
        self.server.execute_command('ZADD', key, score, data)

    def pop(self, timeout=0):
        """
        Pop a request
        timeout not support in this queue class
        """
        # use atomic range/remove using multi/exec
        pipe = self.server.pipeline()
        pipe.multi()
        pipe.zrange(self.key, 0, 0).zremrangebyrank(self.key, 0, 0)
        results, count = pipe.execute()
        if results:
            return self._decode_request(results[0])


class SpiderStack(Base):
    """Per-spider stack"""

    def __len__(self):
        """Return the length of the stack"""
        return self.server.llen(self.key)

    def push(self, request, key=None):
        if key is None:
            key = self.key
        """Push a request"""
        self.server.lpush(key, self._encode_request(request))

    def pop(self, timeout=0):
        """Pop a request"""
        if timeout > 0:
            data = self.server.blpop(self.key, timeout)
            if isinstance(data, tuple):
                data = data[1]
        else:
            data = self.server.lpop(self.key)

        if data:
            return self._decode_request(data)


__all__ = ['SpiderQueue', 'SpiderPriorityQueue', 'SpiderStack']
