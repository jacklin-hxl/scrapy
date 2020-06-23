# -*- coding: utf-8 -*-
import codecs
import json

from scrapy.pipelines.images import ImagesPipeline
import MySQLdb
from twisted.enterprise import adbapi

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


class CnblogPipeline(object):
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


# 获取image名称
class t1ImagePipeline(ImagesPipeline):
    def item_completed(self,results,item,info):
        if "front_image_url" in item:
            image_file_name = ""
            for ok,value in results:
                image_file_name = value["path"]
            item["front_image_name"] = image_file_name

        return item

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

# class MysqlPipline():
#     def __init__(self):
#         self.conn =  MySQLdb.connect("127.0.0.1","root","admin123","cnblog_spider",charset="utf8",use_unicode=True)
#         self.cursor = self.conn.cursor()

#     def process_item(self,item,spider):
#         insert_sql = """
#             insert into t1_cnblog(
#             title,url,url_object_id,front_image_url,parise_nums,comment_nums,fav_nums,tags,content,create_date,front_image_name
#             )
#             values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
#             on duplicate key update
#             title=values(title),
#             front_image_url=values(front_image_url),
#             parise_nums=values(parise_nums),
#             comment_nums=values(comment_nums),
#             fav_nums=values(fav_nums),
#             tags=values(tags),
#             content=values(content),
#             create_date=values(create_date),
#             front_image_name=values(front_image_name)
#             """
#         params = list()
#         params.append(item.get("title",""))
#         params.append(item.get("url",""))
#         params.append(item.get("url_object_id",""))
#         # 转换list为str，否则执行sql报错
#         front_image = "".join(item.get("front_image_url",""))
#         params.append(front_image)
#         params.append(item.get("parise_nums",0))
#         params.append(item.get("comment_nums",0))
#         params.append(item.get("fav_nums",0))
#         params.append(item.get("tags",""))
#         params.append(item.get("content",""))
#         params.append(item.get("create_date","1970-07-01"))
#         params.append(item.get("front_image_name",""))
#         self.cursor.execute(insert_sql,tuple(params))
#         self.conn.commit()
    
#         return item 


