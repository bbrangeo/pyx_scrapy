import logging
import os

import scrapy

from pyx_scrapy.items import ItemK, OutputItem
from pyx_scrapy.utils.consts import MetaK, FILES_PATH

logger = logging.getLogger(__name__)


class NeteaseSongMp3Spider(scrapy.Spider):
    name = 'NeteaseSongMp3'

    url_template = "http://music.163.com/song/media/outer/url?id={song_id}.mp3"

    # def start_requests(self):
    #     kwargs = {
    #         MetaK.PKG: {
    #             MetaK.CP_ID: 1,
    #             MetaK.CP_SONG: "2",
    #             MetaK.CP_ARTIST: "3",
    #             MetaK.REL_ID: 4,
    #         }
    #     }
    #     yield self.create_request(298213, **kwargs)

    @classmethod
    def create_request(cls, song_id, dont_filter=False, *args, **kwargs):
        meta = {
            MetaK.QUEUE_ITEM: {'song_id': song_id},
            MetaK.SPIDER_NAME: cls.name,
        }
        meta.update(kwargs)

        return scrapy.Request(cls.url_template.format(**meta[MetaK.QUEUE_ITEM]), meta=meta, dont_filter=dont_filter)

    def parse(self, response):
        pkg = response.meta.get(MetaK.PKG, {})
        folder = self.settings.get(FILES_PATH)
        folder = folder + os.path.sep + 'netease' + os.path.sep + 'mp3' + os.path.sep
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
