# -*- coding: utf-8 -*-


import redis
import six
from scrapy.utils.misc import load_object

redis_cache = {}


def get_redis_cli(**kw):
    redis_cls_str = kw.pop('redis_cls', None)
    if isinstance(redis_cls_str, six.string_types):
        redis_cls = load_object(redis_cls_str)
        return redis_cls(**kw)
    else:
        port = kw['port']
        host = kw['host']
        db = kw.get('db', 0)
        kw_tuple = (host, port, db)
        if kw_tuple in redis_cache:
            return redis_cache[kw_tuple]
        else:
            r = redis.Redis(**kw)
            redis_cache[kw_tuple] = r
            return r
