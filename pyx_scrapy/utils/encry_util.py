# coding:utf-8


import hashlib


def md5(s, encoding='utf-8'):
    return hashlib.md5(s.encode(encoding)).hexdigest()
