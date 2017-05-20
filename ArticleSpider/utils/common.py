# -*- coding: utf-8 -*-
__author__ = 'pengtuo'


import os
import hashlib


def get_file_dir():
    """获取当前文件的目录路径"""
    return os.path.abspath(os.path.dirname(__file__))


def mkdirs(file):
    prefix = get_file_dir() + '/' + str(file)
    if not os.path.exists(prefix):
        os.mkdir(prefix)
        return prefix
    else:
        return prefix


def get_md5(url):
    """获取url的MD5编码"""
    if isinstance(url, str):
        url = url.encode("utf-8")
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()
