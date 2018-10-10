import logging
import re

import scrapy

from pyx_scrapy.utils.consts import MetaK

logger = logging.getLogger(__name__)


class XiamiSongTransferSpider(scrapy.Spider):
    """
    mid2id
    """
    name = 'XiamiSongTransfer'

    url_template = 'http://www.xiami.com/song/{song_mid}'

    headers = {
        'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8,ru;q=0.6,en;q=0.4,en-US;q=0.2',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'www.xiami.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
        'Cookie': 'x5sec=7b22617365727665723b32223a22663564633737313637343665326664646636653530633261383962663463653743506566754e6746454f4869774a324f6a6571546767453d227d;',
    }

    # def start_requests(self):
    #     return [self.api_create_request(1795583976, dont_filter=True)]

    @classmethod
    def create_request(cls, song_mid, dont_filter=False, *args, **kwargs):
        meta = {
            MetaK.QUEUE_ITEM: {'song_mid': song_mid},
            MetaK.SPIDER_NAME: cls.name,
        }
        meta.update(kwargs)

        return scrapy.Request(cls.url_template.format(**meta[MetaK.QUEUE_ITEM]), meta=meta, dont_filter=dont_filter)

    def parse(self, response):
        pattern = re.compile(
            '<meta name="mobile-agent" content="format=html5; url=http://m.xiami.com/song/(.*?)">')
        song_id = pattern.findall(response.text)[0]
