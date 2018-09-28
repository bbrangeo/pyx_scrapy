# -*- coding: utf-8 -*-

import logging
import re

import scrapy

from pyx_scrapy.spiders.tencent.lossless.tencent_song_info import TencentSongInfoSpider
from pyx_scrapy.utils.consts import MetaK

logger = logging.getLogger(__name__)


class TencentSongIdTransferPageSpider(scrapy.Spider):
    """腾讯歌曲ID抽取MID值"""

    name = "TencentSongIdTransferPage"

    url_template = 'https://y.qq.com/n/yqq/song/{songid}_num.html'

    close_if_idle = False

    def start_requests(self):
        kwargs = {
            MetaK.PKG: {
                MetaK.CP_ID: 10,
                MetaK.CP_SONG: "一朝芳草碧连天",
                MetaK.CP_ARTIST: "爱情悠悠药草香",
                MetaK.REL_ID: 1788526,
            }
        }
        yield self.create_request(1788526, dont_filter=True, **kwargs)

    @classmethod
    def create_request(cls, songid, dont_filter=False, *args, **kwargs):
        meta = {
            MetaK.QUEUE_ITEM: {'songid': songid},
            MetaK.SPIDER_NAME: cls.name
        }
        meta.update(kwargs)
        return scrapy.Request(cls.url_template.format(**meta[MetaK.QUEUE_ITEM]), meta=meta, dont_filter=dont_filter)

    def parse(self, response):
        text = response.text
        fall = re.findall(
            "window\.location\.replace\(\"http://i\.y\.qq\.com/v8/playsong\.html\?ADTAG=newyqq\.song&songmid=([^#]{14})#webchat_redirect",
            text)
        if len(fall) == 1:
            mid = fall[0]

            yield TencentSongInfoSpider.create_request(mid, dont_filter=True,
                                                       **{MetaK.PKG: response.meta.get(MetaK.PKG)})
