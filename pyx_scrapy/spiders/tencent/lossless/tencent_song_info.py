import json
import logging

import scrapy

from pyx_scrapy.spiders.tencent.lossless.tencent_song_file_flac import FlacTencentSongFileSpider
from pyx_scrapy.utils.consts import MetaK

logger = logging.getLogger(__name__)


class FlacTencentSongInfoSpider(scrapy.Spider):
    """腾讯歌曲详细接口爬取spider"""

    name = "FlacTencentSongInfo"

    url_template = 'https://c.y.qq.com/v8/fcg-bin/fcg_play_single_song.fcg?songmid={songmid}&tpl=yqq_song_detail&format=json&g_tk=5381&jsonpCallback=getOneSongInfoCallback&loginUin=0&hostUin=0&format=jsonp&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0'

    @classmethod
    def create_request(cls, mid, dont_filter=False, *args, **kwargs):
        meta = {
            MetaK.QUEUE_ITEM: {
                'songmid': mid
            },
            MetaK.SPIDER_NAME: cls.name
        }
        meta.update({MetaK.PKG: kwargs.get(MetaK.PKG)})
        return scrapy.Request(cls.url_template.format(**dict(meta[MetaK.QUEUE_ITEM])), meta=meta,
                              dont_filter=dont_filter)

    def parse(self, response):
        rjson = json.loads(response.text)

        rdata = rjson.get('data')
        code = int(rjson.get('code'))
        if code == 400:
            return
        if not rdata:
            self.log('songinfo capture error:' + response.text, level=logging.ERROR)
            request = response.request
            retries = request.meta.get('retry_times', 0) + 1
            request.meta['retry_times'] = retries
            if retries < 4:
                return request

        rdata = rdata[0]

        mid = rdata.get('mid')
        if not mid:
            return

        media_mid = rjson.get('data')[0].get('file').get('media_mid')

        # 无损标识
        file = rdata.get('file')
        if file.get('size_flac', 0) > 0 or file.get('size_ape', 0) > 0:
            yield FlacTencentSongFileSpider.create_request(media_mid, dont_filter=True,
                                                           **{MetaK.PKG: response.meta.get(MetaK.PKG)})
