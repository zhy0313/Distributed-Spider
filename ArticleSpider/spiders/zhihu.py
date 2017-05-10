# -*- coding: utf-8 -*-
__author__ = 'pengtuo'


import re
import json
import scrapy
from scrapy.selector import Selector
from ArticleSpider.utils.common import get_captcha

class ZhihuSpider(scrapy.Spider):
    name = "zhihu"
    allowed_domains = ["https://www.zhihu.com"]
    start_urls = ['http://https://www.zhihu.com/']

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
        return [scrapy.Request("https://www.zhihu.com/#signin", headers=self.headers, callback=self.login)]
        
    def login(self, response):
        captcha_bool = get_captcha(self.allowed_domains[0])
        xsrf=''
        xsrf = Selector(response).xpath('//input[@name="_xsrf"]/@value').extract()[0]
        if xsrf:
            post_url = "https://www.zhihu.com/login/phone_num"
            post_data = {
                "_xsrf": xsrf,
                "phone_num": "15652915029",
                "password": "admin123",
                'remember_me': 'true',
                'captcha': input('Input the captcha:')
            }
            return [scrapy.FormRequest(
                url=post_url,
                formdata=post_data,
                headers=self.headers,
                callback=self.check_login,
                dont_filter=True
            )]
        print('未能获得xsrf')

    def check_login(self, response):
        rps = response
        text_json = json.loads(response.text)
        if text_json["r"] != 0:
            print("Login Failed!")
            print("Error info ---> " + text_json["msg"])
        else:
            print("Login success!")
            for url in self.start_urls:
                yield scrapy.Request(url, dont_filter=True, headers=self.headers)
