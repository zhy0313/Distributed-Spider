# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import datetime
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from ArticleSpider.utils.common import extract_num


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class ArticleItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


def remove_comment_tags(value):
    if "评论" in value:
        return ""
    else:
        return value


def return_value(value):
    return value


def deal_create_date(value):
    create_date = value.strip().replace("·", "").strip()
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
        input_processor=MapCompose(extract_num)
    )
    fav_nums = scrapy.Field(
        input_processor=MapCompose(extract_num)
    )
    comment_nums = scrapy.Field(
        input_processor=MapCompose(extract_num)
    )
    tags = scrapy.Field(
        input_processor=MapCompose(remove_comment_tags),
        output_processor=Join(" ")
    )
    content = scrapy.Field()
    
    def get_insert_sql(self):
        insert_sql = """
            insert into article_spider
            (title, create_date, url, url_object_id, front_image_url, front_image_path, praise_nums, fav_nums, comment_nums, tags, content)
            values 
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (self['title'], self['create_date'], self['url'], self['url_id_md5'], 
                self['front_image_url'][0], self['fornt_image_path'], 
                self['praise_nums'], self['fav_nums'],self['comment_nums'], self['tags'], self['content'])

        return insert_sql, params


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

    def get_insert_sql(self):
        insert_sql = """
            insert into zhihu_question
            (question_id, topics, url, title, content, answers_num, comments_num, watch_users_num, clicked_num)
            values 
            (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        question_id = int("".join(self['question_id']))
        topics = ",".join(self['topics'])
        url = self['url'][0]
        title = self['title'][0]
        content = self['content'][0]
        answers_num = extract_num("".join(self['answers_num']))
        comments_num = extract_num("".join(self['comments_num']))
        watch_users_num = int(self['watch_users_num'][0])
        clicked_num = int(self['watch_users_num'][1])

        params = (question_id, topics, url, title,
                  content, answers_num, comments_num, watch_users_num, clicked_num)

        return insert_sql, params


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

    def get_insert_sql(self):
        insert_sql = """
            insert into zhihu_answer
            (answer_id, url, question_id, author_id, content, praise_num, comments_num, create_time, update_time)
            values 
            (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        create_time = datetime.datetime.fromtimestamp(self['create_time']).strftime('%Y-%m-%d %H:%M:%S')
        update_time = datetime.datetime.fromtimestamp(self['update_time']).strftime('%Y-%m-%d %H:%M:%S')

        params = (self['answer_id'], self['url'], self['question_id'], self['author_id'],
                self['content'], self['praise_num'], self['comments_num'], create_time, update_time)

        return insert_sql, params
