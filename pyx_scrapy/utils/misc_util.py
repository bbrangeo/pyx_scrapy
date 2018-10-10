import functools
import hashlib
import json
import logging
import math
import os
import random
import re
import string
from datetime import datetime, date
from decimal import Decimal
from importlib import import_module
from operator import itemgetter

import six

logger = logging.getLogger(__name__)


def loads_jsonp(_jsonp):
    """jsonp字符串转化为json数据"""
    try:
        return json.loads(re.match(".*?({.*}).*", _jsonp, re.S).group(1))
    except:
        raise ValueError('Invalid Input')


def loads_object(path):
    """Load an object given its absolute object path, and return it.

    object can be a class, function, variable or an instance.
    path ie: 'scrapy.downloadermiddlewares.redirect.RedirectMiddleware'
    """

    try:
        dot = path.rindex('.')
    except ValueError:
        raise ValueError("Error loading cls '%s': not a full path" % path)

    module_str, name = path[:dot], path[dot + 1:]
    module_ = import_module(module_str)

    try:
        obj = getattr(module_, name)
    except AttributeError:
        raise NameError("Module '%s' doesn't define any object named '%s'" % (module_str, name))

    return obj


def build_path(s, deep=2):
    """构造文件路径"""

    def _hex2int(ss):
        return int(math.floor(int(ss, 16) / 4))

    ss = hashlib.md5(s.encode()).hexdigest()
    sindex = 0
    step = 3
    sret = ''
    for idx in range(deep):
        eindex = sindex + step
        if eindex > len(ss):
            break
        _s = ss[sindex:eindex]
        sret += str(_hex2int(_s)) + os.path.sep
        sindex = eindex
    return sret


def unicode_escape(s):
    return s.decode('unicode_escape')


def sorted_dictval_key(compdict, reverse=False):
    return [k for k, v in sorted(six.iteritems(compdict), key=itemgetter(1), reverse=reverse)]


def cookies_str2dict_std(cookie_str):
    from http.cookies import SimpleCookie
    cookie = SimpleCookie()
    cookie.load(cookie_str)
    cookies = {}
    for key, morsel in cookie.items():
        cookies[key] = morsel.value
    return cookies


def cookies_str2dict_regex(cookies_str):
    cookies_dict = {}
    fr = re.findall(r"\b([^=]*)=([^;]*);?", cookies_str)
    for item in fr:
        k = item[0]
        v = item[1]
        cookies_dict[k] = v

    return cookies_dict


def slice_with_step(s, step):
    """
    字符串等长切片
    :param s: 
    :param step: 
    :return: 
    """
    ret = []
    index = 0
    while index < len(s):
        ss = ss[index:index + step]
        index += step
        ret.append(ss)
    return ret


def md5(s, encoding='utf-8'):
    return hashlib.md5(s.encode(encoding)).hexdigest()


def filter_empty(dic):
    """
    过滤, 取出None和字符为空的键值
    :param dic:
    :return:
    """
    if not dic:
        return {}
    for key in list(dic.keys()):
        value = dic.get(key)
        if not value:
            del dic[key]
        elif isinstance(value, str) and len(value.strip()) == 0:
            del dic[key]
        elif isinstance(value, list) and len(value) == 0:
            del dic[key]

    return dic


def timeit(clock=True):
    """
    装饰器带参数，再套一层装饰器
    @timeit()  使用时必须带括号
    :param clock:
    :return:

    clock和time的区别
    clock是指CPU真实的执行时间
    time是执行完成总的耗时，包括非运行时间
    """

    def _timeit(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import time
            import inspect  # provide self reflect

            start = time.clock() if clock else time.time()
            ret = func(*args, **kwargs)
            end = time.clock() if clock else time.time()
            logger.info(
                inspect.getmodule(
                    func).__name__ + "." + func.__name__ + ' timeit aop %s time : %s' % (
                    'clock' if clock else 'time', end - start))
            return ret

        return wrapper

    return _timeit


def nonce_generator(length=16):
    """
    随机字符串
    :param length:
    :return:
    """
    chars = string.ascii_letters + string.digits
    s = random.sample(chars, length)
    return "".join(s)


def redirect_script(url):
    return """
        <script language="javascript"type="text/javascript"> 
            window.location.href="%s"; 
        </script>
        """ % url


def obj2serialize(obj):
    if isinstance(obj, datetime):
        return obj.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(obj, date):
        return obj.strftime('%Y-%m-%d')
    elif isinstance(obj, Decimal):
        return "%.2f" % obj
    return obj


class JSONEncoderExt(json.JSONEncoder):
    def default(self, obj):
        r = obj2serialize(obj)
        if type(r) != type(obj):
            return r
        return json.JSONEncoder.default(self, obj)


def r_replace_str(src_str, replace_str, start_str='/', end_str='.'):
    """
    从右开始字符串替换
    :param src_str:
    :param start_str:
    :param end_str:
    :param replace_str:
    :return:
    """
    start_index = src_str.rfind(start_str)
    end_index = src_str.rfind(end_str)
    if end_index == -1:
        end_index = len(src_str)

    find_str = src_str[start_index + 1:end_index]
    return src_str.replace(find_str, replace_str)


def get_current_function_name():
    return inspect.stack()[1][3]


if __name__ == "__main__":
    print(build_path("108661547"))
    print(redirect_script("http://www.baidu.com"))

    dic = {
        "d": Decimal(10.01),
    }
    print(json.dumps(dic, cls=JSONEncoderExt))
