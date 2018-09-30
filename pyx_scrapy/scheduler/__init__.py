# coding:utf-8


class SchedulerDefaultConfs(object):
    QUEUE_CLS = '.queue.FIFOQueue',
    QUEUE_KEY = 'Request:%(spider)s'

    DUPEFILTER_CLS = '.dupefilter.RedisDupeFilter'
    DUPEFILTER_KEY = 'Dupefilter:%(spider)s'

    SUB_MODULE_DUPEFILTER_CLS = '..dupefilter.RedisDupeFilter'
