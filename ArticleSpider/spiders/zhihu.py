# -*- coding: utf-8 -*-
__author__ = 'pengtuo'


import json
import scrapy
import os
import time

class ZhihuSpider(scrapy.Spider):
    name = "zhihu"
    allowed_domains = ["https://www.zhihu.com"]
    start_urls = ['https://www.zhihu.com/']
    login_url = "https://www.zhihu.com/login/phone_num"

    headers = {
        'Accept':'*/*',
        'Accept-Encoding':'gzip: deflate, br',
        'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6,id;q=0.4,zh-TW;q=0.2',
        "Connection": "keep-alive",
        "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.36",
        "Referer": "http://www.zhihu.com/",
        'Host': 'www.zhihu.com'
    }

    def parse(self, response):
        pass

    def start_requests(self):
        return [scrapy.Request("https://www.zhihu.com/#signin",
                               meta={"cookiejar": 1},
                               headers=self.headers,
                               callback=self.request_captcha)]

    def request_captcha(self, response):
        # 获取_xsrf值
        _xsrf = response.css('input[name="_xsrf"]::attr(value)').extract()[0]
        # 获得验证码的地址
        t = str(int(1000 * time.time()))[0:13]
        captcha_url = 'https://www.zhihu.com/captcha.gif?r=' + t + '&type=login'
        # 获取请求
        yield scrapy.Request(
            url=captcha_url,
            headers=self.headers,
            meta={
                "cookiejar": response.meta["cookiejar"],
                "_xsrf": _xsrf
            },
            callback=self.login,
            dont_filter=True
        )

    def login(self, response):
        # 下载验证码
        with open("captcha.gif", "wb") as fp:
            fp.write(response.body)
        # 打开验证码
        os.system('open captcha.gif')
        # 输入验证码
        captcha = input('Input the captcha:')
        # 输入账号和密码
        yield scrapy.FormRequest(
            url=self.login_url,
            headers=self.headers,
            formdata={
                "phone_num": "xxx",
                "password": "xxx",
                "_xsrf": response.meta["_xsrf"],
                "remember_me": "true",
                "captcha": captcha
            },
            meta={
                "cookiejar": response.meta["cookiejar"],
            },
            callback=self.check_login,
            dont_filter=True
        )

    def check_login(self, response):
        text_json = json.loads(response.text)
        if text_json["r"] != 0:
            print("Login Failed!")
            print("Error info ---> " + text_json["msg"])
        else:
            print("Login success!")
            for url in self.start_urls:
                yield scrapy.Request(url, dont_filter=True, headers=self.headers)
