# -*- coding: utf-8 -*-
__author__ = 'pengtuo'


import os
import re
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


def extract_num(value):
    march_re = re.match(r".*(\d+).*", value)
    if march_re:
        nums = int(march_re.group(1))
    else:
        nums = 0
    return nums