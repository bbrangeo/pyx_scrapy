import json
import logging

import scrapy

from pyx_scrapy.spiders.xiami.xiami_song_file import XiamiSongFileSpider
from pyx_scrapy.utils.consts import MetaK, XlsxK

logger = logging.getLogger(__name__)


class XiamiSongInfoSpider(scrapy.Spider):
    name = 'XiamiSongInfo'

    xiami_add_cookie = True

    custom_settings = {
        'COOKIES_ENABLED': True,
    }

    url_template = 'http://{song_id}'

    api = 'mtop.alimusic.music.songservice.getsongdetail'

    # def start_requests(self):
    #     yield self.create_request(2067234)

    @classmethod
    def create_request(cls, song_id, dont_filter=False, *args, **kwargs):
        meta = {
            MetaK.QUEUE_ITEM: {'song_id': song_id},
            MetaK.SPIDER_NAME: cls.name,
            'xiami_h5': {'songId': song_id}
        }
        meta.update(kwargs)

        return scrapy.Request(cls.url_template.format(**meta[MetaK.QUEUE_ITEM]), meta=meta, dont_filter=dont_filter)

    def parse(self, response):
        ctrl = response.meta.get(MetaK.PKG, {}).get(MetaK.CTRL, [])
        json_content = json.loads(response.text)
        ret = json_content.get('ret', [])

        if len(ret) > 0 and ret[0] == 'FAIL_BIZ_GLOBAL_NOT_FOUND::歌曲不存在':
            return

        song_detail = json_content.get('data', {}).get('data', {}).get('songDetail')

        listen_files = song_detail.get('listenFiles', {})

        if XlsxK.xiami_mp3 in ctrl:
            for file in listen_files:
                if file.get('format') == 'mp3' and file.get('quality') == 'h':
                    url = file.get('url')
                    yield XiamiSongFileSpider.create_request(url, **{
                        MetaK.SONG_FILE_FORMAT: file.get("format"),
                        MetaK.PKG: response.meta.get(MetaK.PKG)
                    })
                    break

        if XlsxK.xiami_losses in ctrl:
            for file in listen_files:
                # 下载无损音源
                if file.get('format') == 'wav' or file.get('format') == 'flac' or file.get('format') == 'ape':
                    url = file.get("url")
                    yield XiamiSongFileSpider.create_request(url, **{
                        MetaK.SONG_FILE_FORMAT: file.get("format"),
                        MetaK.PKG: response.meta.get(MetaK.PKG),
                    })
                    break

    # yield XiamiSongLyricSpider.create_request(data[Entity.id])
