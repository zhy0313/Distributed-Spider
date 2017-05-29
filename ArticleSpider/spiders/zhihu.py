# -*- coding: utf-8 -*-
import re
import json
import scrapy
import os
import time
from urllib import parse
from scrapy.loader import ItemLoader
from ArticleSpider.items import ZhihuAnswerItem, ZhihuQuestionItem


# FIXME:爬取的问题与答案详细信息入库后都有信息重复现象，待查
class ZhihuSpider(scrapy.Spider):
    name = "zhihu"
    allowed_domains = ["https://www.zhihu.com"]
    start_urls = ['https://www.zhihu.com/']
    login_url = "https://www.zhihu.com/login/phone_num"
    start_answer_url = 'https://www.zhihu.com/api/v4/questions/{0}/answers?sort_by=default&include=data%5B%2A%5D.is_normal%2Cis_collapsed%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Cmark_infos%2Ccreated_time%2Cupdated_time%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cupvoted_followees%3Bdata%5B%2A%5D.author.badge%5B%3F%28type%3Dbest_answerer%29%5D.topics&limit={1}&offset={2}'

    headers = {
        'Accept':'*/*',
        'Accept-Encoding':'gzip: deflate, br',
        'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6,id;q=0.4,zh-TW;q=0.2',
        "Connection": "keep-alive",
        "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.36",
        "Referer": "http://www.zhihu.com/",
        'authorization': 'oauth c3cef7c66a1843f8b3a9e6a1e3160e20',  # 爬取answer时会有被禁止访问401错误，添加令牌
        'Host': 'www.zhihu.com'
    }

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
        # 验证码
        with open("captcha.gif", "wb") as fp:
            fp.write(response.body)
        os.system('open captcha.gif')
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
                yield scrapy.Request(url, meta={"cookiejar": response.meta["cookiejar"],},
                                     dont_filter=True,
                                     headers=self.headers)

    def parse(self, response):
        all_url = response.css('a::attr(href)').extract()
        all_urls = [parse.urljoin(response.url, url) for url in all_url]
        all_urls = filter(lambda x: True if x.startswith('https') else False, all_urls)
        for url in all_urls:
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", url)
            if match_obj:
                request_url = match_obj.group(1)
                question_id = match_obj.group(2)
                yield scrapy.Request(request_url, headers=self.headers, meta={'question_id': question_id},
                                     dont_filter=True, callback=self.parse_question)
                # break
            else:
                yield scrapy.Request(url, headers=self.headers, dont_filter=True, callback=self.parse)
                # pass

    def parse_question(self, response):
        item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
        question_id = response.meta.get('question_id', 0)
        item_loader.add_value('question_id', question_id)
        item_loader.add_css('topics', '.QuestionHeader-topics .Popover > div::text')
        item_loader.add_value('url', response.url)
        item_loader.add_css('title', '.QuestionHeader-title::text')
        item_loader.add_css('content', '.QuestionHeader-detail')
        item_loader.add_css('answers_num', '.List-headerText span::text')
        item_loader.add_css('comments_num', '.QuestionHeader-Comment button::text')
        item_loader.add_css('watch_users_num', '.NumberBoard-value::text')
        question_item = item_loader.load_item()
        yield question_item
        yield scrapy.Request(self.start_answer_url.format(question_id, 20, 0), headers=self.headers,
                             dont_filter=True,
                             callback=self.parse_answer)

    def parse_answer(self, response):
        # 处理question的answer
        ans_json = json.loads(response.text)
        is_end = ans_json['paging']['is_end']
        next_url = ans_json['paging']['next']

        # 提取answer字段
        answer_item = ZhihuAnswerItem()
        for answer in ans_json['data']:
            answer_item['answer_id'] = answer['id']
            answer_item['url'] = answer['url']
            answer_item['question_id'] = answer['question']['id']
            answer_item['author_id'] = answer['author']['id'] if answer['author']['id'] != '0' else 'anonymous'
            answer_item['content'] = answer['content'] if 'content' in answer else answer['excerpt']
            answer_item['praise_num'] = answer['voteup_count']
            answer_item['comments_num'] = answer['comment_count']
            answer_item['create_time'] = answer['created_time']
            answer_item['update_time'] = answer['updated_time']
            yield answer_item

        if not is_end:
            yield scrapy.Request(next_url, headers=self.headers, dont_filter=True, callback=self.parse_answer)
