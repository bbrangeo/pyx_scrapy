import json
import logging
import re
import time
import traceback
from urllib import request

logger = logging.getLogger(__name__)


class VKeyMp3Middleware:
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
        if not hasattr(spider, 'tencent_vkey_mp3') or not spider.tencent_vkey_mp3:
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


class VKeyFlacMiddleware:
    template_url = 'http://{url}'

    def __init__(self):
        self.vkey = ''
        self.guid = 0
        # key 使用时间限制(s)
        self._key_use_time_limit = 60 * 60
        # 上次获取key的的时间点
        self._last_get_key_time = 0
        # key
        self.key = '8B93466E953B663039D4018EEE753E8078BF6A6976F6E03D1DF29BE48C48DBAB'
        # uin
        self.uin = '251639692'
        # 获取key的url
        self._key_url = 'https://c.y.qq.com/base/fcgi-bin/fcg_music_express_mobile3.fcg?format=json&inCharset=utf8&outCharset=utf-8&cid=205361747&uin=251639692' \
                        '&songmid=002NkERn2LNVI4&filename=M500{media_mid}.mp3&guid={guid}'
        # 要生成的url
        self._url = 'http://isure.stream.qqmusic.qq.com/F000{media_mid}.flac?vkey={vkey}&guid={guid}&uin={uin}&fromtag=48'
        # 备用media_mid
        self._media_mid = ['00012bmI17BvZg', '0002yGou4FsgJ1', '0008cX5s2mGIX5']
        self.stats = None

    @classmethod
    def from_crawler(cls, crawler):
        instance = cls()
        instance.stats = crawler.stats
        return instance

    def process_request(self, request, spider):
        # 忽略请求
        if not hasattr(spider, 'tencent_vkey_flac') or not spider.tencent_vkey_flac:
            return

        logger.debug('request: %s\nnow vkey is %s, already use %.2f s' % (
            request, self.vkey, (time.time() - self._last_get_key_time)))
        try:
            url = self._create_url(request)
            logger.debug('[url]: %s' % url)
        except Exception as e:
            logger.error('create url failed beacuse %s \nreprocess the request' % traceback.format_exc())
            return request
        request._set_url(url)

    def _create_url(self, request):
        media_mid = request.meta['media_mid']
        vkey = self._get_key(media_mid)
        url = self._url.format(**{'media_mid': media_mid, 'vkey': vkey, 'guid': self.guid, 'uin': self.uin})
        return url

    def _get_key(self, media_mid):
        # 没有key或者超过时间限制 生成新的key
        if not self.vkey or not self._check_time():
            self._create_key(media_mid)
        return self.vkey

    def _create_key(self, media_mid):
        logger.info('create tencent client vkey')
        # url_data = {'media_mid': media_mid, 'key': self.key, 'uin': self.uin, 'guid': self.guid,
        #             'time': int(time.time())}
        url_data = {'media_mid': media_mid, 'guid': self.guid, }
        # 'time': int(time.time())}
        count = 0
        while 1:
            try:
                url_data['media_mid'] = self._media_mid[randint(0, 3)]
                res = request.urlopen(self._key_url.format(**url_data)).read()
                self.vkey = json.loads(res.decode('utf-8'))['data']['items'][0]['vkey']
                logger.info('get vkey: ' + self.vkey)
                if not self.vkey.isalnum():
                    logger.debug('get tencent client vkey error, change media_mid retry...')
                    count += 1
                    if count > 5:
                        raise IgnoreRequest
                    time.sleep(5)
                    continue
                break
            except IgnoreRequest:
                return
            except:
                logger.error('get tencent client vkey failed, retry...')
                time.sleep(3)
        logger.debug('[vkey]: %s' % self.vkey)
        print(self._key_url.format(**url_data))
        self._last_get_key_time = time.time()

    def _check_time(self):
        if time.time() - self._last_get_key_time > self._key_use_time_limit:
            return False
        return True
