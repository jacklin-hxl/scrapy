import scrapy
from scrapy.loader import ItemLoader
from zhihu.items import ZhihuQuestionItem,ZhihuQuestionItem

class ZhihuCookiePoolSpider(scrapy.Spider):
    name = 'zhihu_cookie_pool'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']

    headers = {
        "HOST":"www.zhihu.com",
    }

    def parse(self, response):
        """
        提取html页面中所有的url,并跟踪url进一步爬取
        如果提取的url中格式为/question/xxx就下载之后直接进去解析函数
        """

        all_url = response.css("a::attr(href").extract()

    def parse_question(self.response):
        item_loader = ItemLoader(item=ZhihuQuestionItem(),response=response=)
        item_loader.add_css("title","h1.QuestionHeader-title::text").getall()
        ItemLoader.add_css("content",".QuestionHeader-detail .RichText.ztext:text").getall()
        ItemLoader.add_value("url",response.url)
        ItemLoader.add_value("zhihu_id",question_id)
        ItemLoader.css("answer_num","response.css(".QuestionHeader-Comment").get()
        

