import os
import re

import scrapy

from pyx_scrapy.spiders.tencent.lossless.tencent_song_info import FlacTencentSongInfoSpider
from pyx_scrapy.utils.consts import MetaK, FILES_PATH
from pyx_scrapy.utils.gen_requests import xlsx_gen_requests


class FlacTencentSongIdTransferPageSpider(scrapy.Spider):
    """腾讯歌曲ID抽取MID值"""

    name = "FlacTencentSongIdTransferPage"

    url_template = 'https://y.qq.com/n/yqq/song/{songid}_num.html'

    xlsx_name = 'QQFlac.xlsx'

    def start_requests(self):
        filename = os.path.join(self.settings.get(FILES_PATH), self.xlsx_name)
        for (k, kwargs) in xlsx_gen_requests(filename):
            yield self.create_request(k, dont_filter=True, **kwargs)

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

            yield FlacTencentSongInfoSpider.create_request(mid, dont_filter=True,
                                                           **{MetaK.PKG: response.meta.get(MetaK.PKG)})
