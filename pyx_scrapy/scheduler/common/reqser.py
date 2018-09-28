# -*- coding: utf-8 -*-

# 序列化与反序列化request帮助函数

import six

from scrapy.http import Request
from scrapy.utils.python import to_unicode, to_native_str
from collections import OrderedDict

def request_to_dict(request, spider=None):
    """Convert Request object to a dict.

    If a spider is given, it will try to find out the name of the spider method
    used in the callback and store that as the callback.
    """
    cb = request.callback
    if callable(cb):
        cb = _find_method(spider, cb)
    eb = request.errback
    if callable(eb):
        eb = _find_method(spider, eb)
    d = OrderedDict({
        # 'url': to_unicode(request.url),  # urls should be safe (safe_string_url)
        'callback': cb,
        'errback': eb,
        'method': request.method,
        # 'headers': dict(request.headers),
        'body': request.body.decode() if request.body else None,
        'cookies': request.cookies,
        'meta': request.meta,
        '_encoding': request._encoding,
        'priority': request.priority,
        'dont_filter': request.dont_filter,
    })

    # url地址没有参数化，填充url项
    if request.meta.get('queue_item') is None or 'redirect_urls' in request.meta:
        d['url'] = to_unicode(request.url)

    # 为默认值则不序列化
    if d['_encoding'] == 'utf-8':
        del d['_encoding']
    if d['method'] == 'GET':
        del d['method']
    # 删除空的key减少redis内存占用
    for key in list(d.keys()):
        if not d.get(key):
            del d[key]

    return d


def request_from_dict(d, spider=None):
    """Create Request object from a dict.

    If a spider is given, it will try to resolve the callbacks looking at the
    spider for methods with the same name.
    """
    cb = d.get('callback')
    if cb and spider:
        cb = _get_method(spider, cb)
    eb = d.get('errback')
    if eb and spider:
        eb = _get_method(spider, eb)

    url = d.get('url')
    if not url and spider:
        url = spider.url_template.format(**d['meta'].get('queue_item', {}))
    else:
        url = to_native_str(d.get('url'))

    return Request(
        # url=to_native_str(d['url']),
        # url=spider.url_template.format(**d['meta'].get('queue_item', {})),
        url=url,
        callback=cb,
        errback=eb,
        method=d.get('method', 'GET'),
        headers=d.get('headers'),
        body=d.get('body'),
        cookies=d.get('cookies'),
        meta=d.get('meta'),
        encoding=d.get('_encoding', 'utf-8'),
        priority=d.get('priority', 0),
        dont_filter=d.get('dont_filter'))


def _find_method(obj, func):
    if obj:
        try:
            func_self = six.get_method_self(func)
        except AttributeError:  # func has no __self__
            pass
        else:
            if func_self is obj:
                return six.get_method_function(func).__name__
    raise ValueError("Function %s is not a method of: %s" % (func, obj))


def _get_method(obj, name):
    name = str(name)
    try:
        return getattr(obj, name)
    except AttributeError:
        raise ValueError("Method %r not found in: %s" % (name, obj))
