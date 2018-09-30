# coding:utf-8


from pyx_scrapy_exts.const import HEADERS


class HeadersMiddleware(object):

    def process_request(self, request, spider):
        if hasattr(spider, HEADERS):
            request.headers.update(spider.headers)
