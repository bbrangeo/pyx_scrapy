import re

import scrapy

from pyx_scrapy.spiders.tencent.tencent_song_info import TencentSongInfoSpider
from pyx_scrapy.utils.consts import MetaK


class TencentSongTransferSpider(scrapy.Spider):
    """
    id2mid
    """
    name = "TencentSongTransfer"

    url_template = 'https://y.qq.com/n/yqq/song/{songid}_num.html'

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
