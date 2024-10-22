
import json
import re
import datetime
import urllib
import time

import scrapy
from scrapy.loader import ItemLoader
from zhihu.items import ZhihuQuestionItem,ZhihuAnswerItem,ZhihuItemLoader
import redis
from w3lib.html import remove_tags

class ZhihuCookiePoolSpider(scrapy.Spider):
    name = 'zhihu_cookie_pool'
    # 域名不在allowed_domains请求被过滤-Filtered offsite request
    allowed_domains = ['www.zhihu.com','api.zhihu.com']
    # start_urls = ['https://www.zhihu.com/']
    start_urls = ["https://api.zhihu.com/topstory"]
    headers = {
        "HOST": "api.zhihu.com",
        'User-Agent': "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0"
        }
    custom_settings = {
        "COOKIES_ENABLED": True,
        # "DOWNLOAD_DELAY": 5,
        }

    start_answer_url = "https://www.zhihu.com/api/v4/questions/{question_id}/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_labeled%2Cis_recognized%2Cpaid_info%2Cpaid_info_content%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%2A%5D.topics&limit=5&offset=0&platform=desktop&sort_by=default"

    def __init__(self, name=None, **kwargs):
        self.redis_cli = redis.Redis(host="127.0.0.1",port=6379,decode_responses=True,)
        super().__init__(name,**kwargs)
        
    # def parse(self, response):
    #     """
    #     提取html页面中所有的url,并跟踪url进一步爬取
    #     如果提取的url中格式为/question/xxx就下载之后直接进去解析函数
    #     """

    #     all_urls = response.css("a::attr(href)").getall()
    #     all_urls = [urllib.parse.urljoin(response.url, url) for url in all_urls]
    #     all_urls = filter(lambda x:True if x.startswith("https") else False, all_urls)
    #     for url in all_urls:
    #         match_obj = re.search("(.*zhihu.com/question/(\d+))(/|$).*", url)
    #         if match_obj:
    #             #如果提取到question相关的页面则下载后交由提取函数进行提取
    #             request_url = match_obj.group(1)
    #             yield scrapy.Request(request_url, headers=self.headers, callback=self.parse_question)
    #         else:
    #             #如果不是question页面则直接进一步跟踪
    #             yield scrapy.Request(url, headers=self.headers, callback=self.parse)
    def parse(self, response):
        re_data = json.loads(response.text)
        next_url = re_data["paging"]["next"]
        for q in re_data["data"]:
            # 如果为TOPIC_ACKNOWLEDGED_ARTICLE,则不是问题类型
            if q["verb"] == "TOPIC_ACKNOWLEDGED_ANSWER":
                headers = {
                    "HOST": "www.zhihu.com",
                    "Referer": "https://www.zhizhu.com",
                    'User-Agent': "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0",
                    }
                question_answer_id = str(q["target"]["id"])
                create_time = q["target"]["question"]["created"]
                question_id = str(q["target"]["question"]["id"])
                question_url = "https://www.zhihu.com/question/{question_id}/answer/{question_answer_id}".format(question_id=question_id,question_answer_id=question_answer_id)
                yield scrapy.Request(question_url,meta={"create_time":create_time,"question_id":question_id},headers=headers,callback=self.parse_question)
        yield scrapy.Request(next_url, headers=self.headers, callback=self.parse)

    def parse_question(self,response):
        create_time = response.meta.get("create_time","")
        question_id = response.meta.get("question_id","")
        headers = {
            "HOST": "www.zhihu.com",
            "Referer": "https://www.zhizhu.com",
            'User-Agent': "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0"
            }
        # match_obj = re.search("(.*zhihu.com/question/(\d+))(/|$).*", response.url)
        # question_id = int(match_obj.group(2))
        item_loader = ZhihuItemLoader(item=ZhihuQuestionItem(),response=response)
        item_loader.add_css("title","h1.QuestionHeader-title::text")
        item_loader.add_css("content",".QuestionHeader-detail .RichText.ztext::text")
        item_loader.add_value("url",response.url)
        item_loader.add_value("question_id",question_id)
        item_loader.add_css("topics",".QuestionHeader-topics #null-toggle::text")
        item_loader.add_xpath("attention_num","//div[contains(text(),'关注者')]/following-sibling::strong/text()")
        item_loader.add_css("comments_num",".QuestionHeader-Comment button::text")
        item_loader.add_xpath("answer_num","//*[@class='List-headerText']//span/text()[1]")
        item_loader.add_xpath("click_num","//div[contains(text(),'被浏览')]/following-sibling::strong/text()")
        item_loader.add_value("create_time",time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(create_time)))
        item_loader.add_value("crawl_time",str(datetime.datetime.now()))
        question_item = item_loader.load_item()

        yield question_item
        yield scrapy.Request(self.start_answer_url.format(question_id=question_id), headers=headers, callback=self.parse_answer)


    def parse_answer(self,response):
        ans_json = json.loads(response.text)
        # 同一个question下的answer数量太多，只取前五个，否则会影响question的爬取速度
        # is_end = ans_json["paging"]["is_end"]
        # next_url = ans_json["paging"]["next"]
        # headers = {
        #     "HOST": "www.zhihu.com",
        #     "Referer": "https://www.zhizhu.com",
        #     'User-Agent': "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0"
        #     }
        for answer in ans_json["data"]:
            answer_item = ZhihuAnswerItem()
            answer_item["title"] = answer["question"]["title"]
            answer_item["answer_id"] = answer["id"]
            answer_item["url"] = answer["url"]
            answer_item["question_id"] = answer["question"]["id"]
            answer_item["author_id"] = answer["author"]["id"]
            answer_item["content"] = remove_tags(answer["content"])
            answer_item["praise_num"] = answer["voteup_count"]
            answer_item["comments_num"] = answer["comment_count"]
            answer_item["create_time"] = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(answer["created_time"]))
            answer_item["update_time"] = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(answer["updated_time"]))
            answer_item["crawl_time"] = str(datetime.datetime.now())

            yield answer_item

        # if not is_end:
        #     yield scrapy.Request(next_url, headers=headers, callback=self.parse_answer)

    def start_requests(self):
        for url in self.start_urls:
            cookie_str = self.redis_cli.srandmember("zhihu:cookies")
            cookie_dict = json.loads(cookie_str)
            yield scrapy.Request(url, dont_filter=True,headers=self.headers,cookies=cookie_dict)
        

