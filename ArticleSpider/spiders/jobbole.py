# -*- coding: utf-8 -*-
__author__ = 'pengtuo'


import scrapy
from scrapy.http import Request
from urllib import parse
from ArticleSpider.items import JobBoleArticleItem, ArticleItemLoader
from ArticleSpider.utils.common import get_md5


class JobboleSpider(scrapy.Spider):
    """
    伯乐在线爬虫
    """

    name = "jobbole"
    allowed_domains = ["blog.jobbole.com"]
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        """
        1. 提取每篇文章的URL并交给scrapy下载
        2. 提取下一页的URL并交给scrapy
        """

        # 解析列表中的所有文章URL并交给scrapy下载后进行解析
        # //*[@id="archive"]/div[2]/div[1]/a/img
        post_nodes = response.xpath("//*[@id='archive']/div[@class='post floated-thumb']/div[1]/a")
        for post_node in post_nodes:
            post_url = post_node.xpath("@href").extract_first("")
            image_url = post_node.xpath("img/@src").extract_first("")
            yield Request(url=parse.urljoin(response.url, post_url), meta={"front_image_url": image_url}, callback=self.parse_page)

        # 提取下一页的URL并交给scrapy下载
        next_url = response.xpath("//*[@id='archive']/div[21]/a[4]/@href").extract()[0]
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def parse_page(self, response):
        """
        解析文章详情页，提取标题、创建时间、点赞数、收藏数、评论数以及文章标签
        """

        # 通过 itemloader 加载item
        front_image_url = parse.urljoin(response.url, response.meta.get("front_image_url", ""))
        item_loader = ArticleItemLoader(item=JobBoleArticleItem(), response=response)
        item_loader.add_xpath("title", "/html/head/title/text()")
        item_loader.add_xpath("create_date", "//p[@class='entry-meta-hide-on-mobile']/text()")
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_id_md5", get_md5(response.url))
        item_loader.add_value("front_image_url", [front_image_url])
        item_loader.add_xpath("praise_nums", "//span[contains(@class, 'vote-post-up')]/h10/text()")
        item_loader.add_xpath("fav_nums", "//span[@class=' btn-bluet-bigger href-style bookmark-btn  register-user-only ']/text()")
        item_loader.add_xpath("comment_nums", "//a[@href='#article-comment']/span")
        item_loader.add_xpath("tags", "//p[@class='entry-meta-hide-on-mobile']/a/text()")
        item_loader.add_xpath("content", "//div[@class='entry']")

        article_item = item_loader.load_item()

        yield article_item
