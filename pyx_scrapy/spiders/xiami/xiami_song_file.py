import os

import scrapy

from pyx_scrapy.items import OutputItem, ItemK
from pyx_scrapy.utils.consts import MetaK, FILES_PATH


class XiamiSongFileSpider(scrapy.Spider):
    name = 'XiamiSongFile'

    custom_settings = {
        'DOWNLOAD_TIMEOUT': 600,
    }

    @classmethod
    def create_request(cls, url, dont_filter=True, *args, **kwargs):
        meta = {
            MetaK.SPIDER_NAME: cls.name,
        }
        meta.update(kwargs)
        return scrapy.Request(url, meta=meta, dont_filter=dont_filter, priority=0)

    def parse(self, response):
        meta = response.meta
        pkg = meta.get(MetaK.PKG, {})

        if meta.get(MetaK.SONG_FILE_FORMAT) == 'flac' or \
                meta.get(MetaK.SONG_FILE_FORMAT) == 'wav' or \
                meta.get(MetaK.SONG_FILE_FORMAT) == 'ape':
            quiality = 'lossless'
        else:
            quiality = '320'

        folder = self.settings.get(FILES_PATH)
        folder = folder + os.path.sep + 'xiami' + os.path.sep + quiality + os.path.sep
        pathname = '%s-%s.%s' % (pkg.get(MetaK.CP_SONG), pkg.get(MetaK.CP_ARTIST), meta.get(MetaK.SONG_FILE_FORMAT))
        if not os.path.exists(folder):
            os.makedirs(folder)

        with open(folder + pathname, 'wb') as f:
            f.write(response.body)

            item = OutputItem()
            item[ItemK.k] = "csv"
            item[ItemK.pkg] = pkg
            item[ItemK.filename] = pathname
            yield item
