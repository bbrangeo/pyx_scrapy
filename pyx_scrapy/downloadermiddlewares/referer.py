class RefererMiddleware(object):

    def __init__(self, referer):
        self.referer = referer

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        referer = settings.get('REFERER')
        instance = cls(referer)
        cls.instance = instance
        return instance

    def process_request(self, request, spider):
        if not request.headers.get('Referer'):
            referer = self.referer
            if hasattr(spider, 'referer'):
                referer = spider.referer

            request.headers.setdefault('Referer', referer)
