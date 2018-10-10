import json
import logging
import os
import re
from base64 import b64decode

import scrapy

from pyx_scrapy.items import ItemK, OutputItem
from pyx_scrapy.utils.consts import MetaK, FILES_PATH, TEMPLATE_URL_WITH_HTTP

logger = logging.getLogger(__name__)


class TencentSongFlacSpider(scrapy.Spider):
    """腾讯音源抓取spider"""
    name = 'TencentSongFlac'

    tencent_vkey_flac = True

    url_template = TEMPLATE_URL_WITH_HTTP

    @classmethod
    def create_request(cls, media_mid, dont_filter=False, *args, **kwargs):
        meta = {
            MetaK.QUEUE_ITEM: {'url': media_mid},
            MetaK.SPIDER_NAME: cls.name,
            'media_mid': media_mid,
        }
        meta.update({MetaK.PKG: kwargs.get(MetaK.PKG)})
        return scrapy.Request(cls.url_template.format(**meta['queue_item']), meta=meta, dont_filter=dont_filter)

    def parse(self, response):
        pkg = response.meta.get(MetaK.PKG, {})
        folder = self.settings.get(FILES_PATH)
        folder = folder + os.path.sep + 'tencent' + os.path.sep + 'lossless' + os.path.sep
        pathname = '%s-%s.flac' % (pkg.get(MetaK.CP_SONG), pkg.get(MetaK.CP_ARTIST))
        if not os.path.exists(folder):
            os.makedirs(folder)

        with open(folder + pathname, 'wb') as f:
            f.write(response.body)

            item = OutputItem()
            item[ItemK.k] = "csv"
            item[ItemK.pkg] = pkg
            item[ItemK.filename] = pathname
            yield item


class TencentSongMp3Spider(scrapy.Spider):
    """腾讯音源抓取spider"""
    name = 'TencentSongMp3'

    tencent_vkey_mp3 = True

    url_template = TEMPLATE_URL_WITH_HTTP

    @classmethod
    def create_request(cls, media_mid, dont_filter=False, *args, **kwargs):
        meta = {
            MetaK.QUEUE_ITEM: {'url': media_mid},
            MetaK.SPIDER_NAME: cls.name,
            'media_mid': media_mid,
        }
        meta.update(kwargs)

        return scrapy.Request(cls.url_template.format(**meta[MetaK.QUEUE_ITEM]), meta=meta, dont_filter=dont_filter)

    def parse(self, response):
        if response.status == 404 or response.status == 403:
            return
        else:
            pkg = response.meta.get(MetaK.PKG, {})
            folder = self.settings.get(FILES_PATH)
            folder = folder + os.path.sep + 'tencent' + os.path.sep + 'mp3' + os.path.sep
            pathname = '%s-%s.mp3' % (pkg.get(MetaK.CP_SONG), pkg.get(MetaK.CP_ARTIST))
            if not os.path.exists(folder):
                os.makedirs(folder)

            with open(folder + pathname, 'wb') as f:
                f.write(response.body)

                item = OutputItem()
                item[ItemK.k] = "csv"
                item[ItemK.pkg] = pkg
                item[ItemK.filename] = pathname
                yield item


class TencentSongTranslateLrcSpider(scrapy.Spider):
    name = "TencentSongTranslateLrc"

    referer = "https://y.qq.com/n/yqq/playlist/3623096788.html"

    url_template = 'https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_new.fcg?songmid={mid}&g_tk=5381'

    def start_requests(self):
        kwargs = {
            MetaK.PKG: {
                MetaK.CP_ID: 1,
                MetaK.CP_SONG: "2",
                MetaK.CP_ARTIST: "3",
                MetaK.REL_ID: 4,
            }
        }
        yield self.create_request("001OyHbk2MSIi4", **kwargs)

    @classmethod
    def create_request(cls, mid, dont_filter=False, *args, **kwargs):
        meta = {
            MetaK.QUEUE_ITEM: {'mid': mid},
            MetaK.SPIDER_NAME: cls.name,
        }
        meta.update(kwargs)

        return scrapy.Request(cls.url_template.format(**meta[MetaK.QUEUE_ITEM]), meta=meta, dont_filter=dont_filter)

    def parse(self, response):
        pkg = response.meta.get(MetaK.PKG, {})
        folder = self.settings.get(FILES_PATH)
        folder = folder + os.path.sep + 'tencent' + os.path.sep + 'translrc' + os.path.sep
        pathname = '%s-%s.lrc' % (pkg.get(MetaK.CP_SONG), pkg.get(MetaK.CP_ARTIST))
        if not os.path.exists(folder):
            os.makedirs(folder)

        json_str = response.text.replace('MusicJsonCallback(', '')[:-1]

        response = json.loads(json_str)
        tlrc = ""
        try:
            lrc = b64decode(response['lyric']).decode().replace('\n', '\r\n')
            trans = b64decode(response['trans']).decode().replace('\n', '\r\n')
            if not trans:
                logger.info('no trans')
            tlrc = lrc + '\r\n\r\n\r\n\r\n\r\n\r\n' + trans
            tlrc = re.sub(r"(\[\d{2}:\d{2}.\d{2}\])", "", tlrc)
        except Exception as ex:
            logger.exception(ex)
            logger.info(response)

        if not tlrc:
            return

        with open(folder + pathname, 'w', encoding="gb2312") as f:
            f.write(tlrc)

            item = OutputItem()
            item[ItemK.k] = "csv"
            item[ItemK.pkg] = pkg
            item[ItemK.filename] = pathname
            yield item
