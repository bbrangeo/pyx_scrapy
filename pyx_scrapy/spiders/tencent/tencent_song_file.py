# # -*- coding: utf-8 -*-
#
# import os
# import scrapy
# from scrapy import Spider
#
# from krscrapy.utils.consts import MetaKey
# from krscrapy.utils.datetime_util import get_long_time
#
# from krscrapy.utils.misc_util import build_path
# from mzk_spiders.items import MzkSpidersItem, ItemKey
# from mzk_spiders.utils.item_fied import *
# from mzk_spiders.downloadmiddlewares.tencent_addkey import AddKeyMiddleware
# from mzk_spiders.spiders.mzk_merge import MzkMergeSpider
#
#
# class TencentSongFileSpider(Spider):
#     """腾讯音源抓取spider"""
#     name = 'TencentSongFile'
#
#     close_if_idle = False
#     add_key = True
#     url_template = AddKeyMiddleware.template_url
#     is_run = True
#     ignore_status_list = []
#     allow_status_list = [404, 200, 201, 403]
#     # custom_settings = {
#     #     'SPIDER_MIDDLEWARES': {
#     #         'scrapy.spidermiddlewares.httperror.HttpErrorMiddleware': None,
#     #         # 'krscrapy.spidermiddlewares.httperror.HttpErrorExtMiddleware': None,
#     #     }
#     # }
#
#     def start_requests(self):
#         control = {"isMQ":"song_import","topic":"mzk-merge-topic-t","isFile": 1, "isEchoprint": 1}
#         return [self.create_request('000ynik02WA2v0', 201694122, dont_filter=True, **{MetaKey.CONTROL: control})]
#
#     @classmethod
#     def create_request(cls, media_mid, song_id, dont_filter=False, *args, **kwargs):
#         assert isinstance(song_id, int)
#         meta = {'queue_item': {'url': media_mid}, 'spider_name': cls.name, 'media_mid': media_mid,
#                 'data': {Song.id: song_id}}
#         meta.update(kwargs)
#         return scrapy.Request(cls.url_template.format(**meta['queue_item']), meta=meta, dont_filter=dont_filter)
#
#     @classmethod
#     def create_request_echoprint(cls, media_mid, song_id, song_mid, dont_filter=False, *args, **kwargs):
#         assert isinstance(song_id, int)
#         meta = {'queue_item': {'url': media_mid}, 'spider_name': cls.name, 'media_mid': media_mid,
#                 'data': {Song.id: song_id, Song.mid: song_mid, 'media_mid': media_mid}}
#         meta.update(kwargs)
#         return scrapy.Request(cls.url_template.format(**meta['queue_item']), meta=meta, dont_filter=dont_filter,
#                               priority=get_long_time())
#
#     def parse(self, response):
#         data = response.meta.get('data', {})
#         control = response.meta.get(MetaKey.CONTROL, {})
#         control['site'] = Site.tencent
#         song_id = data.get(Song.id)
#         if response.status == 404 or response.status == 403:
#             data[Song.haveFile] = False
#             yield MzkSpidersItem.create_item(Site.tencent, Type.song, data)
#             if control.get('topic') == self.settings.get('MERGE_TOPIC'):
#                 yield MzkMergeSpider.create_request('tencent', song_id, data, dont_filter=True, **{MetaKey.CONTROL: control})
#         else:
#             # data = response.meta.get('data', {})
#             # song_id = data.get(Song.id)
#             if control.get('topic') == self.settings.get('MERGE_TOPIC'):
#                 folder = self.settings.get('MERGE_SONG_FILE_PATH')
#                 control.pop(Song.isEchoprint, None)
#             else:
#                 folder = self.settings.get('SAVE_SONG_FILE_PATH')
#             folder = folder + os.path.sep + 'tencent' + os.path.sep + 'mp3' + os.path.sep
#             subpath = build_path(str(song_id))
#             path = subpath + str(song_id) + '.mp3'
#             if not os.path.exists(folder + subpath):
#                 os.makedirs(folder + subpath)
#
#             with open(folder + path, 'wb') as f:
#                 f.write(response.body)
#
#             data['mp3_path'] = path
#             data[Song.haveFile] = True
#
#             if os.path.getsize(folder + path) == 0:
#                 return
#             if control.get('topic') == self.settings.get('MERGE_TOPIC'):
#                 yield MzkMergeSpider.create_request(Site.tencent, song_id, data, dont_filter=True, **{MetaKey.CONTROL: control})
#             else:
#                 yield MzkSpidersItem.create_item(Site.tencent, Type.song, data)
#             # 指纹请求入队
#             if Song.isEchoprint in control:
#                 meta = {Song.id: song_id, Song.mid: data.get(Song.mid),
#                         "media_mid": data.get('media_mid'), 'mp3_path': data['mp3_path']}
#                 meta['spider_name'] = 'echoprint'
#                 meta.update(**{MetaKey.CONTROL: control})
#                 yield scrapy.Request(self.url_template.format(**{'url': song_id}), meta=meta, dont_filter=True,
#                                      priority=get_long_time())
