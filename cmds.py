from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from pyx_scrapy.spiders.tencent.mp3.tencent_song_id_transfer_page import *
from pyx_scrapy.spiders.tencent.mp3.tencent_song_info import *
from pyx_scrapy.spiders.tencent.mp3.tencent_song_file import *

from pyx_scrapy.spiders.tencent.lossless.tencent_song_id_transfer_page import *
from pyx_scrapy.spiders.tencent.lossless.tencent_song_info import *
from pyx_scrapy.spiders.tencent.lossless.tencent_song_file_flac import *

import import4pyinstaller

def v1multi_crawler():
    settings = get_project_settings()

    # pyinstaller 加载有问题，只能手动引入class
    # spider_loader = SpiderLoader(_settings)
    # spider_names = spider_loader.list()
    # spider_loader.list()

    spider_names = [
        Mp3TencentSongIdTransferPageSpider, Mp3TencentSongInfoSpider, Mp3TencentSongFileSpider,
        FlacTencentSongFileSpider, FlacTencentSongIdTransferPageSpider, FlacTencentSongInfoSpider,
    ]

    crawler_process = CrawlerProcess(settings)
    for spider_name in spider_names:
        print("+++++++++++  %s +++++++++++++++" % spider_name)
        crawler_process.crawl(spider_name)

    crawler_process.start()


if __name__ == "__main__":
    v1multi_crawler()
