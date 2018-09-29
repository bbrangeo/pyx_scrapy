import json
import logging
import re
import time
import traceback
from urllib import request

logger = logging.getLogger(__name__)


class AddKeyMiddleware:
    template_url = 'http://{url}'

    def __init__(self):
        self.key = ''
        self.guid = 0
        # key 使用时间限制(s)
        self._key_use_time_limit = 60 * 60
        # 上次获取key的的时间点
        self._last_get_key_time = 0
        # 获取key的url
        self._key_url = 'https://c.y.qq.com/base/fcgi-bin/fcg_music_express_mobile3.fcg?format=json&inCharset=utf8&outCharset=utf-8&cid=205361747&uin=251639692' \
                        '&songmid=002NkERn2LNVI4&filename=M500%s.mp3&guid=%s'
        # 要生成的url
        self._url = 'http://dl.stream.qqmusic.qq.com/M500{media_mid}.mp3?vkey={vkey}&guid=%s&fromtag=30' % self.guid
        self.stats = None

    @classmethod
    def from_crawler(cls, crawler):
        instance = cls()
        instance.stats = crawler.stats
        return instance

    def process_request(self, request, spider):
        # 忽略请求
        if not hasattr(spider, 'add_key') or not spider.add_key:
            return
        logger.debug('request: %s\nnow vkey is %s, already use %.2f s' % (
            request, self.key, (time.time() - self._last_get_key_time)))
        try:
            url = self._create_url(request)
            logger.debug('[url]: %s' % url)
        except Exception as e:
            logger.error('create url failed beacuse %s \nreprocess the request' % traceback.format_exc())
            return request
        request._set_url(url)

    def _create_url(self, request):
        media_mid = request.meta['media_mid']
        key = self._get_key(media_mid)
        url = self._url.format(**{'media_mid': media_mid, 'vkey': key})
        return url

    def _get_key(self, media_mid):
        # 没有key或者超过时间限制 生成新的key
        # if not self.key or not self._check_time():
        self._create_key(media_mid)
        return self.key

    def _create_key(self, media_mid):
        logger.info('create tencent vkey')
        while 1:
            try:
                res = request.urlopen(self._key_url % (media_mid, self.guid), timeout=5).read()
                break
            except:
                logger.error('get tencent vkey failed, retry...')
                time.sleep(3)
        self.key = json.loads(re.findall(r'.*?({.*}).*', res.decode('utf-8'))[0])['data']['items'][0]['vkey']
        logger.debug('[vkey]: %s' % self.key)
        self._last_get_key_time = time.time()

    def _check_time(self):
        if time.time() - self._last_get_key_time > self._key_use_time_limit:
            return False
        return True
