# coding:utf-8
from scrapy.crawler import CrawlerProcess
from scrapy.spiderloader import SpiderLoader
from scrapy.utils.project import get_project_settings
import logging

import scrapy.core.scheduler
import scrapy.core.engine
import scrapy.core.scraper
import scrapy.core.spidermw
import scrapy.core.downloader
import scrapy.core.downloader.contextfactory
import scrapy.core.downloader.handlers.http

import scrapy.spiderloader
import scrapy.statscollectors
import scrapy.logformatter
import scrapy.dupefilters
import scrapy.squeues
import scrapy.pipelines

import scrapy.extensions.spiderstate
import scrapy.extensions.corestats
import scrapy.extensions.telnet
import scrapy.extensions.logstats
import scrapy.extensions.memusage
import scrapy.extensions.memdebug
import scrapy.extensions.feedexport
import scrapy.extensions.closespider
import scrapy.extensions.debug
import scrapy.extensions.httpcache
import scrapy.extensions.statsmailer
import scrapy.extensions.throttle

import scrapy.downloadermiddlewares.stats
import scrapy.downloadermiddlewares.httpcache
import scrapy.downloadermiddlewares.cookies
import scrapy.downloadermiddlewares.useragent
import scrapy.downloadermiddlewares.httpproxy
import scrapy.downloadermiddlewares.ajaxcrawl
import scrapy.downloadermiddlewares.decompression
import scrapy.downloadermiddlewares.defaultheaders
import scrapy.downloadermiddlewares.downloadtimeout
import scrapy.downloadermiddlewares.httpauth
import scrapy.downloadermiddlewares.httpcompression
import scrapy.downloadermiddlewares.redirect
import scrapy.downloadermiddlewares.retry
import scrapy.downloadermiddlewares.robotstxt
import scrapy.spidermiddlewares.depth
import scrapy.spidermiddlewares.httperror
import scrapy.spidermiddlewares.offsite
import scrapy.spidermiddlewares.referer
import scrapy.spidermiddlewares.urllength

import pyx_scrapy_exts.scheduler.redis.scheduler
import pyx_scrapy_exts.scheduler.redis.queue
import pyx_scrapy_exts.scheduler.dupefilter
import pyx_scrapy_exts.downloadermiddlewares
import pyx_scrapy_exts.downloadermiddlewares.useragent
import pyx_scrapy_exts.downloadermiddlewares.headers

import redis
import pandas

logger = logging.getLogger(__name__)


def v1multi_crawler():
    _settings = get_project_settings()
    spider_loader = SpiderLoader(_settings)
    spider_names = spider_loader.list()
    logger.info("++++++ loaders ++++++", spider_names)

    # spider_names = ['TencentSongFileFlac']

    crawler_process = CrawlerProcess(_settings)
    for spider_name in spider_names:
        logger.info("+++++++++++  %s +++++++++++++++" % spider_name)
        crawler_process.crawl(spider_name)

    crawler_process.start()


if __name__ == "__main__":
    v1multi_crawler()
