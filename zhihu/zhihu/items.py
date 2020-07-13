# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import scrapy
from scrapy.loader.processors import Join, MapCompose,TakeFirst,Identity
from scrapy.loader import ItemLoader


class ZhihuItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class ZhihuItemLoader(ItemLoader):
    topics_in = Identity()
    topics_out = Join(",")
    default_output_processor = TakeFirst()

def handle_num(value):
    if value != "添加评论":
        value = int(value.replace(",",""))
        return value
    else:
        return 0

def extract_num(value):
    value = value.split(" ")[0]
    return value

def take_seconde(values):
    for value in values:
        value = value
    return value

class ZhihuQuestionItem(scrapy.Item):
    question_id = scrapy.Field()
    topics = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    comments_num = scrapy.Field(input_processor=MapCompose(extract_num,handle_num))
    answer_num = scrapy.Field(input_processor=MapCompose(handle_num),)
    attention_num = scrapy.Field(input_processor=MapCompose(handle_num),)
    click_num = scrapy.Field(input_processor=MapCompose(handle_num),)
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
            insert into zhihu_question(
            question_id,topics,url,title,content,answer_num,comments_num,attention_num,click_num,crawl_time
            )
            values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            on duplicate key update
            title=values(title),
            content=values(content),
            answer_num=values(answer_num),
            comments_num=values(comments_num),
            attention_num=values(attention_num),
            click_num=values(click_num),
            topics=values(topics),
            question_id=values(question_id)
        """
        params = []
        params.append(self.get("question_id",""))
        params.append(self.get("topics",""))
        params.append(self.get("url",""))
        params.append(self.get("title",""))
        params.append(self.get("content",""))
        params.append(self.get("answer_num",-1))
        params.append(self.get("comments_num",-1))
        params.append(self.get("attention_num",-1))
        params.append(self.get("click_num",-1))
        params.append(self.get("crawl_time","1970-01-01 00:00:00"))

        return insert_sql,params

class ZhihuAnswerItem(scrapy.Item):
    answer_id = scrapy.Field() 
    url = scrapy.Field() 
    question_id = scrapy.Field()
    author_id = scrapy.Field()
    content = scrapy.Field()
    parise_num = scrapy.Field()
    comments_num = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
            insert into zhihu_answer(
            answer_id,question_id,url,author_id,content,parise_num,comments_num,create_time,update_time,crawl_time
            )
            values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            on duplicate key update
            content=values(content),
            parise_num=values(answer_num),
            comments_num=values(comments_num),
            update_time=values(update_time),
            crawl_time=values(crawl_time),
        """
        params = []
        params.append(self.get("answer_id",""))
        params.append(self.get("question_id",""))
        params.append(self.get("url",""))
        params.append(self.get("author_id",""))
        params.append(self.get("content",""))
        params.append(self.get("parise_num",-1))
        params.append(self.get("comments_num",-1))
        params.append(self.get("create_time","1970-01-01 00:00:00"))
        params.append(self.get("update_time","1970-01-01 00:00:00"))
        params.append(self.get("crawl_time","1970-01-01 00:00:00"))


        return insert_sql,params
