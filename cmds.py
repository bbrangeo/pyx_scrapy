import os
import pathlib

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from pyx_scrapy.scheduler import SchedulerDefaultConfs
from pyx_scrapy.scheduler.queue import SpiderShareQueue
from pyx_scrapy.spiders.tencent.tencent_song_file import Mp3TencentSongFileSpider, FlacTencentSongFileSpider
from pyx_scrapy.spiders.tencent.tencent_song_info import TencentSongInfoSpider
from pyx_scrapy.spiders.tencent.tencent_song_starter import TencentSongStarterSpider
from pyx_scrapy.utils.consts import XlsxK, FILES_PATH, MetaK
from pyx_scrapy.utils.gen_requests import xlsx_gen_requests


def v1multi_crawler():
    settings = get_project_settings()

    # >>>>>>>>>>>>>>>>> 加载数据 >>>>>>>>>>>>>>>>>>>
    spider4xlsx = {
        TencentSongStarterSpider: [
            XlsxK.tencent_flac,
            XlsxK.tencent_mp3
        ]
    }
    queue = SpiderShareQueue(settings, None, None)
    for spider_clz, filenames in spider4xlsx.items():
        kid2pkg = {}

        for fn in filenames:
            pathfilename = os.path.join(settings.get(FILES_PATH), fn)
            if pathlib.Path(pathfilename).exists():
                for (kid, kwargs) in xlsx_gen_requests(pathfilename):
                    if kid in kid2pkg:
                        kid2pkg.get(kid).get(MetaK.PKG).get(MetaK.CTRL).append(fn)
                    else:
                        kwargs.get(MetaK.PKG).update({MetaK.CTRL: [fn]})
                        kid2pkg.update({kid: kwargs})

        for _kid, _pkg in kid2pkg.items():
            request = spider_clz.create_request(_kid, **_pkg)
            queue.push(request, SchedulerDefaultConfs.QUEUE_KEY % {'spider': request.meta['spider_name']})
    # <<<<<<<<<<<<<<<<<<<< 加载数据 <<<<<<<<<<<<<<<<<<<<<

    # pyinstaller 加载有问题,SpiderLoader是运行时扫描，spiders没有被主动打包 => 【pyinstaller 不能语义化打包，只能静态打包】
    # spider_loader = SpiderLoader(_settings)
    # spider_names = spider_loader.list()
    # spider_loader.list()

    spider_cls = [
        TencentSongStarterSpider, TencentSongInfoSpider, Mp3TencentSongFileSpider,
        FlacTencentSongFileSpider
    ]

    crawler_process = CrawlerProcess(settings)

    for spider_clz in spider_cls:
        print("+++++++++++  %s +++++++++++++++" % spider_clz)
        crawler_process.crawl(spider_clz)

    crawler_process.start()


if __name__ == "__main__":
    v1multi_crawler()
