# -*- coding: utf-8 -*-
__author__ = 'pengtuo'


import os
import re
import hashlib
import urllib
import urllib.request
import imghdr
import http.cookiejar as cookielib


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


def get_captcha(base_url):
    """获取网站登录验证码图片
    @params
        base_url:需要获取的网站域名，格式'www.xxx.com'
    """
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookielib.LWPCookieJar()))
    base_dir = get_file_dir()
    site = re.match('.*www.(.*).com', base_url).group(1)
    if site == "zhihu":
        captcha_url = base_url + '/captcha.gif?type=login'
        print(captcha_url)
        picture = opener.open(captcha_url).read()
        imgtype = imghdr.what('', h=picture)
        if not imgtype:
            imgtype = 'txt'
        captcha_file = mkdirs('zhihu_captcha') + '/{}.{}'.format('captcha', imgtype)
        if os.path.exists(captcha_file):
            os.remove(captcha_file)
        local = open(captcha_file, 'wb')
        local.write(picture)
        local.close()
        return True

if __name__ == '__main__':
    # print(get_md5("http://www.zhihu.com"))
    # print(get_file_dir())
    get_captcha('http://www.zhihu.com')
    # store_dir = mkdirs('zhihu_captcha')
