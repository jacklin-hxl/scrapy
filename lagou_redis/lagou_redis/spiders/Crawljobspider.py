# -*- coding: utf-8 -*-
import time
import pickle
import os
from datetime import datetime

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy_redis.spiders import RedisCrawlSpider
from lagou_redis.items import LagouRedisItem,LagouRedisItemLoader
from lagou_redis.utils.common import get_md5

class CrawljobspiderSpider(RedisCrawlSpider):
    name = 'Crawljobspider'
    allowed_domains = ['www.lagou.com']
    # start_urls = ['http://https://www.lagou.com//']
    redis_key = 'CrawljobspiderSpider:start_urls'

    rules = (
        Rule(LinkExtractor(allow=r'jobs/\d+.html'),callback='parse_job', follow=True),
    )

    def parse_job(self, response):
        item_loader = LagouRedisItemLoader(item=LagouRedisItem(),response=response)
        item_loader.add_css("title",".job-name::attr(title)")
        item_loader.add_value("url",response.url)
        item_loader.add_value("url_object_id",get_md5(response.url))
        item_loader.add_css("salary",".job_request .salary::text")
        item_loader.add_xpath("job_city","//*[@class='job_request']//span[2]/text()")
        item_loader.add_xpath("work_years","//*[@class='job_request']//span[3]/text()")
        item_loader.add_xpath("degree_need","//*[@class='job_request']//span[4]/text()")
        item_loader.add_xpath("job_type","//*[@class='job_request']//span[5]/text()")
        item_loader.add_css("tags",".job_request .position-label .labels::text")
        item_loader.add_css("publish_time",".publish_time::text")
        item_loader.add_css("job_advantage",".job-advantage p::text")
        item_loader.add_css("job_desc",".job_bt div ")
        item_loader.add_css("job_addr",".work_addr")
        item_loader.add_css("company_name","#job_company img::attr(alt)")
        item_loader.add_css("company_url","#job_company dt a::attr(href)")
        item_loader.add_value("crawl_date",datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        job_item = item_loader.load_item()
        return job_item

    def start_requests(self):
        cookies = []
        if os.path.exists("lagou_redis/cookies/lagou.cookie"):
            cookies = pickle.load(open("lagou_redis/cookies/lagou.cookie","rb"))
        if not cookies:
            from selenium import webdriver
            browser = webdriver.Chrome(executable_path="lagou_redis/webdriver/chromedriver.exe")
            browser.get("https://passport.lagou.com/login/login.html")
            browser.find_element_by_css_selector(".form_body .input.input_white").send_keys("18355053764")
            browser.find_element_by_css_selector(".form_body input[type='password']").send_keys("2468gggg")
            browser.find_element_by_css_selector(".form_body input[type='submit']").click()
            time.sleep(15)
            cookies = browser.get_cookies()
            pickle.dump(cookies,open('lagou_redis/cookies/lagou.cookie',"wb"))

        cookie_dict = {}
        for cookie in cookies:
            cookie_dict[cookie["name"]] = cookie["value"]

        for url in self.start_urls:
            yield scrapy.Request(url, dont_filter=True,cookies=cookie_dict)