import os

import scrapy

from pyx_scrapy.downloadermiddlewares.tencent_addkey import AddKeyMiddleware
from pyx_scrapy.items import OutputItem, ItemK
from pyx_scrapy.utils.consts import FILES_PATH
from pyx_scrapy.utils.consts import MetaK


class Mp3TencentSongFileSpider(scrapy.Spider):
    """腾讯音源抓取spider"""
    name = 'Mp3TencentSongFile'

    tencent_vkey_mp3 = True

    url_template = AddKeyMiddleware.template_url

    ignore_status_list = []

    allow_status_list = [404, 200, 201, 403]

    # def start_requests(self):
    #     return [self.create_request('000ynik02WA2v0', dont_filter=True)]

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
