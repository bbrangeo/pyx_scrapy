# -*- coding: utf-8 -*-

# 自定义去重

import logging
import time

from scrapy.dupefilters import BaseDupeFilter

from pyx_scrapy.utils import get_redis_cli
from pyx_scrapy.utils.encry_util import md5

DEFAULT_DUPEFILTER_KEY = "dupefilter:%(timestamp)s"

logger = logging.getLogger(__name__)


# TODO: Rename class to RedisDupeFilter.
class SSDBDupeFilter(BaseDupeFilter):
    """Redis-based request duplicates filter.

    This class can also be used with default Scrapy's scheduler.

    """

    logger = logger
    _instance = None

    def __init__(self, settings, key, debug=False):
        """Initialize the duplicates filter.

        Parameters
        ----------
        server : redis.StrictRedis
            The redis server instance.
        key : str
            Redis key Where to store fingerprints.
        debug : bool, optional
            Whether to log filtered requests.

        """
        self.server = get_redis_cli(**settings.get('SSDB_CONFIG', {}))
        self.key = key
        self.debug = debug
        self.logdupes = True
        # 获取过期时间，没有配置默认是60天，毫秒
        self.expired_time_length = settings.get('EXPIRED_TIME_LENGTH', 1000 * 60 * 60 * 24 * 60)

    @classmethod
    def from_settings(cls, settings, key, debug=False):
        if not cls._instance:
            cls._instance = cls(settings, key=key, debug=debug)
        return cls._instance

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        key = DEFAULT_DUPEFILTER_KEY % {'timestamp': int(time.time())}
        debug = settings.getbool('DUPEFILTER_DEBUG')
        return cls.from_settings(settings, key, debug)

    def request_seen(self, request, key=None):
        """Returns True if request was already seen.

        Parameters
        ----------
        request : scrapy.http.Request

        Returns
        -------
        bool

        """
        if key is None:
            key = self.key
        fp = self.request_fingerprint(request)
        value = self.server.hget(key, fp)
        # This returns the number of values added, zero if already exists.
        # 判断是否存在存在的话是否过期
        now_time = int(time.time() * 1000)
        if not value:
            added = self.server.hset(key, fp, now_time)
            return added != 1
        value = int(value.decode())
        if value == 1:
            self.server.hset(key, fp, now_time)
            logger.info('%s fingerprint value == 1 init to now time %s' % (fp, now_time))
            return False
        else:
            if now_time - value > self.expired_time_length:
                self.server.hset(key, fp, now_time)
                return False
            else:
                logger.info('%s fingerprint not expired' % fp)
                return True
                # added = self.server.hset(key, fp, 1)
                # return added == 0

    def request_fingerprint(self, request):
        return md5(request.url)

    def close(self, reason=''):
        """Delete data on close. Called by Scrapy's scheduler.

        Parameters
        ----------
        reason : str, optional

        """
        self.clear()

    def clear(self):
        """Clears fingerprints data."""
        self.server.delete(self.key)

    def log(self, request, spider):
        """Logs given request.

        Parameters
        ----------
        request : scrapy.http.Request
        spider : scrapy.spiders.Spider

        """
        if self.debug:
            msg = "Filtered duplicate request: %(request)s"
            self.logger.debug(msg, {'request': request}, extra={'spider': spider})
        elif self.logdupes:
            msg = ("Filtered duplicate request %(request)s"
                   " - no more duplicates will be shown"
                   " (see DUPEFILTER_DEBUG to show all duplicates)")
            msg = "Filtered duplicate request: %(request)s"
            self.logger.debug(msg, {'request': request}, extra={'spider': spider})
            self.logdupes = False
