# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import scrapy
from scrapy.loader.processors import Join, MapCompose,TakeFirst,Identity,Compose
from scrapy.loader import ItemLoader
from models.es_types import ZhihuAnswerType,ZhihuQuestionType
from elasticsearch_dsl.connections import connections
es = connections.create_connection(ZhihuQuestionType._doc_type.using)
class ZhihuItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class ZhihuItemLoader(ItemLoader):
    topics_in = Identity()
    topics_out = Join(",")
    default_input_processor = TakeFirst()
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
def gen_suggests(index,info_tuple):
    used_words = set()
    suggests = []
    anylyzed_words = set()
    for text,weight in info_tuple:
        if text:
            # 调用es的analy
            words = es.indices.analyze(index=index,analyzer="ik_max_word",params={'filter':["lowercase"]},body=text)["tokens"]
            for r in words:
                if len(r["token"])>1:
                    anylyzed_words.add(r["token"])
            # anylyzed_words = set([r["token"] for r in words if len(r["token"])>1])
            new_words = anylyzed_words - used_words
        else:
            new_words = set()
        if new_words:
            suggests.append({"input":list(new_words),"weight":weight})

    return suggests
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
        params.append(self.get("answer_num",0))
        params.append(self.get("comments_num",0))
        params.append(self.get("attention_num",0))
        params.append(self.get("click_num",0))
        params.append(self.get("crawl_time","1970-01-01 00:00:00"))

        return insert_sql,params

    def save_to_es(self):
        article = ZhihuQuestionType()
        article.question_id = self.get("question_id","")
        article.topics = self.get("topics","")
        article.url = self.get("url","")
        article.title = self.get("title","")
        article.content = self.get("content","")
        article.answer_num = self.get("answer_num",0)
        article.comments_num = self.get("comments_num",0)
        article.attention_num = self.get("attention_num",0)
        article.click_num = self.get("click_num",0)
        article.crawl_time = self.get("crawl_time","1970-01-01 00:00:00")

        article.suggest = gen_suggests(article._doc_type.index,((article.title,10),(article.topics,7),(article.content,4)))
        article.save()

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
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
            insert into zhihu_answer(
            answer_id,question_id,url,author_id,content,praise_num,comments_num,create_time,update_time,crawl_time
            )
            values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            on duplicate key update
            content=values(content),
            praise_num=values(praise_num),
            comments_num=values(comments_num),
            update_time=values(update_time),
            crawl_time=values(crawl_time)
        """
        params = []
        params.append(self.get("answer_id",""))
        params.append(self.get("question_id",""))
        params.append(self.get("url",""))
        params.append(self.get("author_id",""))
        params.append(self.get("content",""))
        params.append(self.get("praise_num",0))
        params.append(self.get("comments_num",0))
        params.append(self.get("create_time","1970-01-01 00:00:00"))
        params.append(self.get("update_time","1970-01-01 00:00:00"))
        params.append(self.get("crawl_time","1970-01-01 00:00:00"))

        return insert_sql,params

    def save_to_es(self):
        article = ZhihuAnswerType()
        article.answer_id = self.get("answer_id","")
        article.question_id = self.get("question_id","")
        article.url = self.get("url","")
        article.author_id = self.get("author_id","")
        article.content = self.get("content","")
        article.praise_num = self.get("praise_num",0)
        article.comments_num = self.get("comments_num",0)
        article.create_time = self.get("create_time","1970-01-01 00:00:00")
        article.update_time = self.get("update_time","1970-01-01 00:00:00")
        article.crawl_time = self.get("crawl_time","1970-01-01 00:00:00")

        article.suggest = gen_suggests(article._doc_type.index,((article.content,10),))

        article.save()
        