import json
import logging
import threading

from pyx_scrapy_exts.scheduler import reqser
from queuelib.queue import FifoMemoryQueue

logger = logging.getLogger(__name__)

lock = threading.Lock()


class SpiderShareQueue:
    k2queue = {}

    def __init__(self, settings, spider, key, serializer=None, request_reqser=None):
        self.settings = settings
        self.spider = spider
        self.key = key

        if serializer is None:
            serializer = json
        if not hasattr(serializer, 'loads'):
            raise TypeError("serializer does not implement 'loads' function: %r" % serializer)
        if not hasattr(serializer, 'dumps'):
            raise TypeError("serializer '%s' does not implement 'dumps' function: %r" % serializer)
        self.serializer = serializer

        if request_reqser is None:
            request_reqser = reqser
        if not hasattr(request_reqser, 'request_to_dict'):
            raise TypeError("request_reqser does not implement 'request_to_dict' function: %r" % request_reqser)
        if not hasattr(request_reqser, 'request_from_dict'):
            raise TypeError(
                "request_reqser '%s' does not implement 'request_from_dict' function: %r" % request_reqser)
        self.request_reqser = request_reqser

    @classmethod
    def from_settings(cls, settings, spider, key, serializer=None, request_reqser=None):
        return cls(settings, spider, key, serializer, request_reqser)

    def _encode_request(self, request):
        obj = self.request_reqser.request_to_dict(request, self.spider)
        return self.serializer.dumps(obj)

    def _decode_request(self, encoded_request):
        obj = self.serializer.loads(encoded_request)
        return self.request_reqser.request_from_dict(obj, self.spider)

    def __len__(self):
        queue = self.k2queue.get(self.key, None)
        if queue:
            return len(queue)
        return 0

    def push(self, request, key=None):
        if not key:
            key = self.key
        logger.debug("push %s ### %s", key, request)
        data = self._encode_request(request)
        if key in self.k2queue:
            self.k2queue[key].push(data)
        else:
            if lock.acquire():
                try:
                    if key not in self.k2queue:
                        queue = FifoMemoryQueue()
                        queue.push(data)
                        self.k2queue.update({key: queue})
                    else:
                        self.k2queue[key].push(data)
                finally:
                    lock.release()

    def pop(self):
        queue = self.k2queue.get(self.key, None)
        if queue:
            result = queue.pop()
            if result:
                req = self._decode_request(result)
                logger.debug("pop %s ### %s", self.key, req)
                return req
