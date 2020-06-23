# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import Join, MapCompose,TakeFirst,Identity
from scrapy.loader import ItemLoader

class CnblogItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class t1ItemLoader(ItemLoader):
    default_output_processor = TakeFirst()
    tags_in = Identity()
    tags_out = Join(",")
    front_image_url_out = Identity()

def handler_create_date(value):
    import re
    match_re = re.match(".*?(\d+.*)",value[0])
    if match_re:
        result = match_re.group(1)
        return result
    # else:
    #     return "1970-01-01 00:00"

class t1Item(scrapy.Item):
    title = scrapy.Field()
    create_date = scrapy.Field(input_processor=handler_create_date)
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field()
    commentcount = scrapy.Field()
    burycount = scrapy.Field()
    diggcount = scrapy.Field()
    totalview = scrapy.Field()
    tags = scrapy.Field()
    content = scrapy.Field()
    front_image_name = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
            insert into t1_cnblog(
            title,url,url_object_id,front_image_url,diggcount,totalview,commentcount,burycount,tags,content,create_date,front_image_name
            )
            values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            on duplicate key update
            title=values(title),
            front_image_url=values(front_image_url),
            diggcount=values(diggcount),
            totalview=values(totalview),
            burycount=values(burycount),
            commentcount=values(commentcount),
            tags=values(tags),
            content=values(content),
            create_date=values(create_date),
            front_image_name=values(front_image_name)
        """
        params = []
        params.append(self.get("title",""))
        params.append(self.get("url",""))
        params.append(self.get("url_object_id",""))
        # 转换list为str，否则执行sql报错
        front_image = "".join(self.get("front_image_url",""))
        params.append(front_image)
        params.append(self.get("diggcount",0))
        params.append(self.get("totalview",0))
        params.append(self.get("commentcount",0))
        params.append(self.get("burycount",0))
        params.append(self.get("tags",""))
        params.append(self.get("content",""))
        params.append(self.get("create_date","1970-01-01 00:00:00"))
        params.append(self.get("front_image_name",""))

        return insert_sql,params