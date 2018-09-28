import inspect
import functools
import json
import datetime


def __get_current_function_name():
    return inspect.stack()[2][3]


def get_current_function_name():
    return inspect.stack()[1][3]


def middleware_process_stats(func):
    @functools.wraps(func)
    def wrapper(*args, **kw):
        request = kw.get('request')
        response = kw.get('response')
        if not request and not response:
            return func(*args, **kw)
        if not request:
            request = response.request
        self = args[0]
        spider = kw.get('spider')
        if not spider:
            spider = self.spider
        if self.stats:
            self.stats._add_process(json.dumps(request.meta.get('queue_item')),
                                    self.__class__.__name__ + ':' + __get_current_function_name() + '==' + str(datetime.datetime.now()),
                                    spider.name)
        return func(*args, **kw)

    return wrapper
