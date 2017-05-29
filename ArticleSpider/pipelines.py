# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json
import MySQLdb
import MySQLdb.cursors
from scrapy.pipelines.images import ImagesPipeline
from scrapy import signals
from twisted.enterprise import adbapi


class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item


class JsonWithEncodingPipeline(object):
    """
    将数据保存到本地json文件
    """

    # 写格式打开文件
    def __init__(self):
        self.file = codecs.open('scraped_data.json', 'w', encoding='utf-8')

    # 爬虫的分析结果都会由scrapy交给此函数处理
    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(line)
        return item

    # 爬虫关闭触发关闭文档
    def spider_closed(self, spider):
        self.file.close()


class MysqlStorePipeline(object):
    """
    同步存储入数据库
    """

    def __init__(self):
        self.conn = MySQLdb.connect('127.0.0.1', 'root', '', 'JobBoleSpider', charset='utf8', use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = """
            insert into jobbole_article(title, url, url_object_id, tags)
            values (%s, %s, %s ,%s)
        """
        self.cursor.execute(insert_sql, (item['title'], item['url'], item['url_id_md5'],  item['tags']))
        self.conn.commit()


class MysqlTwistedStorePipeline(object):
    """
    利用twisted库异步存储入数据库
    """

    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        db_args = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool('MySQLdb', **db_args)
        return cls(dbpool)

    def process_item(self, item, spider):
        query = self.dbpool.runInteraction(self.do_upinsert, item)
        query.addErrback(self.handle_error, item, spider)

    def do_upinsert(self, cursor, item):
        insert_sql, params = item.get_insert_sql()
        cursor.execute(insert_sql, params)

    def handle_error(self, failure, item, spider):
        print('******************** ERROR **********************')
        print(item['url'])
        print(failure)


class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        if "front_image_url" in item:
            for ok, value in results:
                image_file_path = value['path']
            item['fornt_image_path'] = image_file_path

        return item
