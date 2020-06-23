# -*- coding: utf-8 -*-
import codecs
import json

import MySQLdb
from twisted.enterprise import adbapi

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


class LagouRedisPipeline(object):
    def process_item(self, item, spider):
        return item

# 序列化item于本地
class JsonWithEncodingPipeline(object):
    # def __init__(self):
    #     self.file = codecs.open("t1.json","a",encoding="utf-8")
    def open_spider(self,spider):
        self.file = codecs.open("t1.json","a",encoding="utf-8")
    # 如果它返回的是Item对象，那么此Item会被低优先级的Item Pipeline的process_item()方法处理，直到所有的方法被调用完毕。
    # 如果它抛出的是DropItem异常，那么此Item会被丢弃，不再进行处理。
    def process_item(self,item,spider):
        lines = json.dumps(dict(item),ensure_ascii=False) + "\n"
        self.file.write(lines)
        return item 

    def close_spider(self,spider):
        self.file.close()




class MysqlTwistedPipline():
    def __init__(self,dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls,settings):
        from MySQLdb.cursors import DictCursor
        dbparams = dict(
            host=settings["MYSQL_HOST"],
            db=settings["MYSQL_DBNAME"],
            user=settings["MYSQL_USER"],
            passwd=settings["MYSQL_PASSWORD"],
            charset='utf8',
            use_unicode=True,
            cursorclass=DictCursor,
        )
        dbpool = adbapi.ConnectionPool("MySQLdb",**dbparams)
        return cls(dbpool)

    def process_item(self,item,spider):
        query = self.dbpool.runInteraction(self.do_insert,item)
        query.addErrback(self.handler_error,item,spider)

    def handler_error(self,failue,item,spider):
        print(failue)

    def do_insert(self,cursor,item):
        insert_sql,params = item.get_insert_sql()
        cursor.execute(insert_sql,tuple(params))
        return item