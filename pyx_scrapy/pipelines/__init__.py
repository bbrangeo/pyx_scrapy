# coding:utf-8

import logging

logger = logging.getLogger(__name__)

"""
1.pipeline中spider.name的应用。pipeline中的process_item中可以根据spider.name来对不同的item进行不同的处理
if spider return multi type item ,is not useful, classify item is better way

2.多个pipeline处理一个item。
pipeline中的process_item方法必须返回一个item或者raise一个DropItem的异常，
如果返回item的话这个item将会被之后的pipeline接收到
"""
