import json
import logging
import re
import time
import traceback
from urllib import parse, request

from twisted.internet import task

from pyx_scrapy.utils.misc_util import md5

logger = logging.getLogger(__name__)


class AddCookieMiddleware:
    reset_url = 'http://{url}'

    def __init__(self):
        # cookie 使用时间限制(s)
        self.cookie_time_limit = 600
        # cokie 使用次数限制
        self.cookie_use_times_limit = 500
        # 上次获取cookie的的时间点
        self.cookie_time = 0
        # 当前 cookie 使用次数
        self.cookie_use_times = 0
        self.cookie = ''
        self.token = ''
        self.cookie_url = 'http://acs.m.xiami.com/h5/mtop.alimusic.music.list.ranklistservice.getranks/1.0/'
        self.url = 'https://h5api.m.xiami.com/h5/%s/1.0/?dataType=json&t=%s&appKey=12574478&sign=%s&api=%s&v=1.0&type=originaljson&data=%s'
        # 参数
        self.data = {
            'header':
                {"platformId": "win",
                 'appId': 200,
                 # "accessToken": "49bc063b76ce37ac8c5d8a191eab1cf5",
                 "openId": 286235960,
                 "network": 1,
                 "appVersion": 3010200,
                 "resolution": "1178*704",
                 "remoteIp": "192.168.64.1",
                 "callId": 1522144033953,
                 "sign": '3bd427556b0ce50d7908b87b715bc3b4',
                 "deviceId": 'Wu Na Neng Xiao De',
                 "utdid": "Wu Na Neng Xiao De",
                 },
            'model': '',
        }

        self.log_interval = 10
        self.failed_times_limit = 10
        t = task.LoopingCall(self._log)
        t.start(self.log_interval)

    @classmethod
    def from_crawler(cls, crawler):
        instance = cls()
        return instance

    def process_request(self, request, spider):
        # 忽略请求
        if not hasattr(spider, 'xiami_add_cookie') or not spider.xiami_add_cookie:
            return
        # 找到需要生成url的request
        if 'xiami_h5' in request.meta:
            # 检测cookie时间
            self._check_time()
            # 检测cookie次数
            self._check_use_times()
            self.data['model'] = request.meta['xiami_h5']
            self.data['header']['callId'] = int(time.time() * 1000)
            self.data['header']['sign'] = md5(
                json.dumps(self.data['model']).replace(' ', '') + str(self.data['header']['callId']))
            data = json.dumps({'requestStr': json.dumps(self.data)})
            try:
                url = self._create_url(spider.api, data, self.token)
            except Exception as e:
                logger.exception(e)
                logger.error('create url failed beacuse %s \nreprocess the request' % traceback.format_exc())
                return request
            request._set_url(url)
            request.cookies = self.cookie
            request.headers.update({
                'Accept': 'application/json',
                'Accept-Language': 'zh-CN',
                'Connection': 'keep-alive',
                'Content-type': 'application/x-www-form-urlencoded',
                'Host': 'h5api.m.xiami.com',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) XIAMI-MUSIC/3.0.7 Chrome/56.0.2924.87 Electron/1.6.11 Safari/537.36'
            })

            self.cookie_use_times += 1

    def process_response(self, request, response, spider):
        if hasattr(spider, 'add_cookie'):
            # 请求不成功
            # retcode = response.headers['M-Retcode']
            retcode = response.headers['x-aserver-sret']
            # 不成功 并且不是因为服务器抽风 重置这个request
            if retcode != b'SUCCESS' and retcode != b'FAIL_BIZ_GLOBAL_SYSTEM_ERROR':
                logger.warning('reset the request [%s] because [%s]' % (request, response.headers['M-Retcode']))
                new_request = self._reset_request(request, response)
                return new_request
        return response

    def _create_url(self, api, data, token):
        q_data = self._quote_data(data)
        now = int(time.time() * 1000)
        sign = md5('%s&%s&12574478&%s' % (token, now, data))
        return self.url % (api, now, sign, api, q_data)

    @staticmethod
    def _quote_data(data):
        return parse.quote(data)

    @staticmethod
    def _parse_cookie(cookie):
        if cookie == '':
            logger.info('cookie is none')
            return 0
        cookie1 = re.findall(r'_m_h5_tk=(.*?);', cookie[0])[0]
        cookie2 = re.findall(r'_m_h5_tk_enc=(.*?);', cookie[1])[0]
        cookie = {'_m_h5_tk': cookie1, '_m_h5_tk_enc': cookie2}
        # cookie1 = '743cb6ee84fddbe9e64a539dc50508fb_1519632840401'
        # cookie2 = 'ed3d8fe3332e15f07ed7dfd8ee36a44a'
        # cookie = {'_m_h5_tk': cookie1, '_m_h5_tk_enc': cookie2}
        token = cookie1.split('_')[0]
        logger.debug('cookie: %s, token:%s' % (cookie, token))
        return cookie, token

    def _get_cookie(self):
        logger.info('[get_cookie] get the cookie')
        req = request.Request(self.cookie_url, None, {
            'Accept': 'application/json',
            'Accept-Language': 'zh-CN',
            'Connection': 'keep-alive',
            'Content-type': 'application/x-www-form-urlencoded',
            'Host': 'acs.m.xiami.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) XIAMI-MUSIC/3.0.2 Chrome/51.0.2704.106 Electron/1.2.8 Safari/537.36'
        })
        try:
            response = request.urlopen(req)
        except Exception as e:
            logger.exception(e)
            logger.info('[get_cookie] get response faild')
            logger.info('[get_cookie] try get cookie again')
            self._get_cookie()
            return
        logger.info('[get_cookie] get cookie success')
        cookies = response.headers.get_all('set-cookie')
        self.cookie, self.token = self._parse_cookie(cookies)
        self.cookie_time = time.time()
        self.cookie_use_times = 0

    def _check_time(self):
        if not self.cookie:
            logger.info('no cookie')
            self._get_cookie()
            return
        if time.time() - self.cookie_time > self.cookie_time_limit:
            logger.info('over time limit, change the cookies')
            self._get_cookie()

    def _check_use_times(self):
        if self.cookie_use_times > self.cookie_use_times_limit:
            logger.info('over cookie use time limit, change the cookies')
            self._get_cookie()

    def _reset_request(self, request, response=None):
        meta = request.meta
        failed_times = meta.get('failed_times', 0)
        logger.warning('raquest failed %s times' % failed_times)
        if failed_times > self.failed_times_limit:
            return response
            # raise IgnoreRequest
        meta['failed_times'] = failed_times + 1
        return request.replace(url=self.reset_url, dont_filter=True, meta=meta)

    def _log(self):
        logger.info(
            'cookie use times: %s/%s, last cookie : %s' % (
                self.cookie_use_times, self.cookie_use_times_limit, self.cookie_time
            )
        )
