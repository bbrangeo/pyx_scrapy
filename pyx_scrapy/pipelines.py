import csv
import os

from pyx_scrapy.items import ItemK
from pyx_scrapy.utils.consts import MetaK, FILES_PATH


class OutputCSVPipeline(object):
    FILES_PATH = ""

    def __init__(self):
        filename = os.path.join(self.FILES_PATH, "output.csv")
        self.file = open(filename, mode="a", newline="")
        self.writer = csv.writer(self.file)

    @classmethod
    def from_crawler(cls, crawler):
        cls.FILES_PATH = crawler.settings.get(FILES_PATH, "")
        pipe = cls()
        pipe.crawler = crawler
        return pipe

    def process_item(self, item, spider):
        if ItemK.k in item and "csv" == item[ItemK.k]:
            pkg = item[ItemK.pkg]
            self.writer.writerow((
                spider.name,
                pkg.get(MetaK.CP_ID), pkg.get(MetaK.CP_SONG), pkg.get(MetaK.CP_ARTIST),
                pkg.get(MetaK.REL_ID), item[ItemK.filename]
            ))
            self.file.flush()
        return item

    def spider_closed(self, spider):
        self.file.close()
