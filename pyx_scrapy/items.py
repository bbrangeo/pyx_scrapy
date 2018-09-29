import scrapy


class ItemK:
    k = "k"
    pkg = "pkg"
    filename = "filename"


class OutputItem(scrapy.Item):
    k = scrapy.Field()
    pkg = scrapy.Field()
    filename = scrapy.Field()
