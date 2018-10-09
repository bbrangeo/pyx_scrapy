import logging

logger = logging.getLogger(__name__)


class UrlMiddleware(object):

    def process_request(self, request, spider):
        logger.info(request.url)
