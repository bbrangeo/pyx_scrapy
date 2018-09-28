# -*- coding: utf-8 -*-

import os

import scrapy
from pyx_scrapy.downloadermiddlewares.tencent_addkey_client import AddKeyClientMiddleware
from scrapy import Spider


class TencentSongFileFlacSpider(Spider):
    """腾讯音源抓取spider"""
    name = 'TencentSongFileFlac'

    close_if_idle = False
    add_key_client = True
    url_template = AddKeyClientMiddleware.template_url
    is_run = True

    def start_requests(self):
        yield self.create_request('0006Ve8a2zEDSA', 1788526, dont_filter=True)

    @classmethod
    def create_request(cls, media_mid, song_id, dont_filter=False, *args, **kwargs):
        assert isinstance(song_id, int)
        meta = {
            'queue_item': {'url': media_mid},
            'spider_name': cls.name,
            'media_mid': media_mid,
        }
        meta.update(kwargs)
        return scrapy.Request(cls.url_template.format(**meta['queue_item']), meta=meta, dont_filter=dont_filter)

    def parse(self, response):
        folder = self.settings.get('SAVE_FILE_PATH')
        folder = folder + os.path.sep + 'tencent' + os.path.sep + 'lossless' + os.path.sep
        path = 'a.flac'
        if not os.path.exists(folder):
            os.makedirs(folder)

        with open(folder + path, 'wb') as f:
            f.write(response.body)
