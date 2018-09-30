import scrapy
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

import pyx_scrapy
import pyx_scrapy.settings
import pyx_scrapy.pipelines

import pyx_scrapy.downloadermiddlewares.tencent_addkey
import pyx_scrapy.downloadermiddlewares.tencent_addkey_client
# import pyx_scrapy.spiders
# import pyx_scrapy.spiders.tencent
# import pyx_scrapy.spiders.tencent.mp3
# import pyx_scrapy.spiders.tencent.mp3.tencent_song_file
# import pyx_scrapy.spiders.tencent.mp3.tencent_song_id_transfer_page
# import pyx_scrapy.spiders.tencent.mp3.tencent_song_info

#

import redis

