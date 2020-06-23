# -*- coding: utf-8 -*-
from w3lib.html import remove_tags

from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst,MapCompose,Join,Identity
import scrapy
# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html




class LagouRedisItemLoader(ItemLoader):
    default_output_processor = TakeFirst()
    tags_out = Identity()


def remove_splash(value):
    # 去掉/
    return value.replace("/","")

def mystrip(value):
    # 去掉首位空格
    return value.strip()

# def remove_space(value):
#     import unicodedata
#     value = unicodedata.normalize('NFKC',value)
#     return value

def mysplit(value):
    # 去除\xa0
    return value.split()[0]

def handle_jobaddr(value):
    addr_list = value.split("\n")
    addr_list = [item.strip() for item in addr_list if item.strip() != "查看地图"]
    return "".join(addr_list)

class LagouRedisItem(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    salary = scrapy.Field(input_processor=MapCompose(remove_splash,mystrip),)
    job_city = scrapy.Field(input_processor=MapCompose(remove_splash,mystrip),)
    work_years = scrapy.Field(input_processor=MapCompose(remove_splash,mystrip),)
    degree_need = scrapy.Field(input_processor=MapCompose(remove_splash,mystrip),)
    job_type = scrapy.Field(input_processor=MapCompose(remove_splash,mystrip),)
    publish_time = scrapy.Field(input_processor=MapCompose(remove_splash,mystrip,mysplit),)
    job_advantage = scrapy.Field(input_processor=MapCompose(remove_splash,mystrip),)
    job_desc = scrapy.Field(input_processor=MapCompose(remove_tags,remove_splash,mystrip),)
    job_addr = scrapy.Field(input_processor=MapCompose(remove_tags,handle_jobaddr),)
    company_name = scrapy.Field(input_processor=MapCompose(remove_splash,mystrip),)
    company_url = scrapy.Field()
    tags = scrapy.Field(input_processor=Join(","))
    crawl_date = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
            INSERT INTO lagou_redis_job(url_object_id,url,title,salary,job_city,work_years,degree_need,job_type,
            publish_time,job_advantage,job_desc,job_addr,company_name,company_url,tags,crawl_date)
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE salary=VALUES(salary),job_desc=VALUES(job_desc),crawl_date=VALUES(crawl_date),work_years=VALUES(work_years)
        """
        params = (
            self["url_object_id"],self["url"],self["title"],self["salary"],self["job_city"],self["work_years"],
            self["degree_need"],self["job_type"],self["publish_time"],self["job_advantage"],self["job_desc"],
            self["job_addr"],self["company_name"],self["company_url"],self["tags"],self["crawl_date"],
        )

        return insert_sql,params