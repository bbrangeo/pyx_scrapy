import os

import scrapy

from pyx_scrapy.items import ItemK, OutputItem
from pyx_scrapy.utils.consts import MetaK, FILES_PATH, TEMPLATE_URL_WITH_HTTP


class FlacTencentSongFileSpider(scrapy.Spider):
    """腾讯音源抓取spider"""
    name = 'FlacTencentSongFile'

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
        pathname = '%s.flac' % (pkg.get(MetaK.CP_SONG) + "-" + pkg.get(MetaK.CP_ARTIST))
        if not os.path.exists(folder):
            os.makedirs(folder)

        with open(folder + pathname, 'wb') as f:
            f.write(response.body)

            item = OutputItem()
            item[ItemK.k] = "csv"
            item[ItemK.pkg] = pkg
            item[ItemK.filename] = pathname
            yield item


class Mp3TencentSongFileSpider(scrapy.Spider):
    """腾讯音源抓取spider"""
    name = 'Mp3TencentSongFile'

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
            pathname = '%s.mp3' % (pkg.get(MetaK.CP_SONG) + "-" + pkg.get(MetaK.CP_ARTIST))
            if not os.path.exists(folder):
                os.makedirs(folder)

            with open(folder + pathname, 'wb') as f:
                f.write(response.body)

                item = OutputItem()
                item[ItemK.k] = "csv"
                item[ItemK.pkg] = pkg
                item[ItemK.filename] = pathname
                yield item
