# -*- coding: utf-8 -*-
import scrapy
from ArticleSpider.items import LagouItemLoader, LagouJobItem
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from ArticleSpider.utils.common import get_md5


# FIXME:爬取一定数量就重定位到登陆界面，待查，拟采用模拟登陆解决
class LagouSpider(CrawlSpider):
    name = 'lagou'
    allowed_domains = ['www.lagou.com']
    start_urls = ['https://www.lagou.com/']

    rules = (
        Rule(LinkExtractor(allow=r'zhaoping/.*'), follow=True),
        Rule(LinkExtractor(allow=r'gongsi/j\d+.html'), follow=True),
        Rule(LinkExtractor(allow=r'jobs/\d+.html'), callback='parse_job', follow=True),
    )

    def parse_start_url(self, response):
        return []

    def process_results(self, response, results):
        return results

    def parse_job(self, response):
        i = {}
        item_loader = LagouItemLoader(item=LagouJobItem(), response=response)
        item_loader.add_xpath('title', '//div[@class="job-name"]/@title')
        item_loader.add_value('url', response.url)
        item_loader.add_value('url_object_id', get_md5(url=response.url))
        item_loader.add_xpath('salary', '//span[@class="salary"]/text()')
        item_loader.add_xpath('job_city', '//*[@class="job_request"]/p/span[2]/text()')
        item_loader.add_xpath('work_years', '//*[@class="job_request"]/p/span[3]/text()')
        item_loader.add_xpath('degree_need', '//*[@class="job_request"]/p/span[4]/text()')
        item_loader.add_xpath('job_type', '//*[@class="job_request"]/p/span[5]/text()')
        item_loader.add_xpath('publish_time', '//*[@class="publish_time"]/text()')
        item_loader.add_css('tags', '.position-label li::text')
        item_loader.add_xpath('job_advantage', '//*[@class="job-advantage"]/p/text()')
        item_loader.add_xpath('job_desc', '//*[@class="job_bt"]/div')
        item_loader.add_xpath('company_url', '//*[@class="job_company"]/dt/a/@href')
        item_loader.add_xpath('company_name', '//*[@class="job_company"]/dt/a/img/@alt')

        job_item = item_loader.load_item()

        return job_item
