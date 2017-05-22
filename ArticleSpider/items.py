# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
# import datetime
import re
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class ArticleItemLoader(ItemLoader):
    default_output_processor=TakeFirst()


def remove_comment_tags(value):
    if "评论" in value:
        return ""
    else:
        return value


def return_value(value):
    return value


def get_nums(value):
    march_re = re.match(r".*(\d+).*", value)
    if march_re:
        nums = int(march_re.group(1))
    else:
        nums = 0
    return nums


def deal_create_date(value):
    create_date = value.strip().replace("·","").strip()
    return create_date


class JobBoleArticleItem(scrapy.Item):
    title = scrapy.Field()
    create_date = scrapy.Field(
        input_processor=MapCompose(deal_create_date)
    )
    url = scrapy.Field()
    url_id_md5 = scrapy.Field()
    front_image_url = scrapy.Field(
        output_processor=MapCompose(return_value)
    )
    fornt_image_path = scrapy.Field()
    praise_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    fav_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    comment_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    tags = scrapy.Field(
        input_processor=MapCompose(remove_comment_tags),
        output_processor=Join(" ")
    )
    content = scrapy.Field()

class ZhihuQuestionItem(scrapy.Item):
    question_id = scrapy.Field()
    topics = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    answers_num = scrapy.Field()
    comments_num = scrapy.Field()
    watch_users_num = scrapy.Field()
    clicked_num = scrapy.Field()


class ZhihuAnswerItem(scrapy.Item):
    answer_id = scrapy.Field()
    url = scrapy.Field()
    question_id = scrapy.Field()
    author_id = scrapy.Field()
    content = scrapy.Field()
    praise_num = scrapy.Field()
    comments_num = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()

