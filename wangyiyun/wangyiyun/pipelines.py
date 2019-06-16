# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql


# 连接mysql
class MySQLPipeline(object):
    def __init__(self, db, host, port, user, password):
        self.db = db
        self.host = host
        self.port = port
        self.user = user
        self.password = password

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            db=crawler.settings.get('MYSQL_DB_NAME', 'crawler'),
            host=crawler.settings.get('MYSQL_HOST', 'localhost'),
            port=crawler.settings.get('MYSQL_PORT', 3306),
            user=crawler.settings.get('MYSQL_USER', 'root'),
            password=crawler.settings.get('MYSQL_PASSWORD', 'qq87863932')
        )

    def open_spider(self, spider):
        self.db_conn = pymysql.connect(host=self.host, port=self.port, password=self.password,
                                       user=self.user, db=self.db, charset='utf8')
        self.db_cur = self.db_conn.cursor()

    def close_spider(self, spider):
        self.db_conn.close()

    def process_item(self, item, spider):
        data = dict(item)
        keys = ','.join(data.keys())
        values = ','.join(['%s']*len(data))
        sql = 'INSERT INTO %s (id,%s) VALUES(default,%s)' % (item.table, keys, values)
        self.db_cur.execute(sql, tuple(data.values()))
        self.db_conn.commit()
        return item

