import re

import scrapy

from pyx_scrapy.spiders.tencent.mp3.tencent_song_info import Mp3TencentSongInfoSpider
from pyx_scrapy.utils.consts import MetaK


class Mp3TencentSongIdTransferPageSpider(scrapy.Spider):
    """腾讯歌曲ID抽取MID值"""

    name = "Mp3TencentSongIdTransferPage"

    url_template = 'https://y.qq.com/n/yqq/song/{songid}_num.html'

    close_if_idle = False

    def start_requests(self):
        # filename = os.path.join(self.settings.get(FILES_PATH), 'QQMp3.xlsx')
        # xlsx = pandas.read_excel(filename)
        # for item in xlsx.values:
        #     kwargs = {
        #         MetaK.PKG: {
        #             MetaK.CP_ID: item[0],
        #             MetaK.CP_SONG: item[1],
        #             MetaK.CP_ARTIST: item[2],
        #             MetaK.REL_ID: item[3],
        #         }
        #     }
        #     yield self.create_request(item[0], dont_filter=True, **kwargs)
        yield self.create_request(4997277, dont_filter=True, **{
            MetaK.PKG: {
                MetaK.CP_ID: 10,
                MetaK.CP_SONG: "一朝芳草碧连天",
                MetaK.CP_ARTIST: "爱情悠悠药草香",
                MetaK.REL_ID: 4997277,
            }})

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

            yield Mp3TencentSongInfoSpider.create_request(mid, dont_filter=True,
                                                          **{MetaK.PKG: response.meta.get(MetaK.PKG)})
