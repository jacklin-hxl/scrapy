# -*- coding: utf-8 -*-
import re
from urllib import parse
import json

import scrapy
from cnblog.items import t1Item,    
from cnblog.utils.common import get_md5
from scrapy.loader import ItemLoader

class T1Spider(scrapy.Spider):
    name = 't1'
    allowed_domains = ['news.cnblogs.com']
    start_urls = ['https://news.cnblogs.com/']

    def parse(self, response):
        '''
        1.获取新闻url交给scrapy下载器解析
        2.获取下页的新闻urls
        '''
        # url = response.xpath('//*[@id="news_list"]//h2[@class="news_entry"]/a/@href').extract()
        # urls = response.css('#news_list h2.news_entry a::attr(href)').extract()
        post_nodes = response.css('#news_list .news_block')[:8]
        for post_node in post_nodes:
            post_url = post_node.css('h2 a::attr(href)').extract_first("")
            if post_node.css('.entry_summary a img::attr(src)').extract_first(""):
                image_url = response.urljoin(post_node.css('.entry_summary a img::attr(src)').extract_first(""))
            else:
                image_url = ""
            yield scrapy.Request(url=parse.urljoin(response.url,post_url),meta={'front_image_url':image_url},callback=self.parse_detail)
        
        # next_url = response.xpath('//a[contains(text(),"Next >")]/@href').extract_first("")
        # yield scrapy.Request(url=parse.urljoin(response.url,next_url),callback=self.parse)
    # 详情页的数据爬取
    def parse_detail(self,response):
        # 判断是否是新闻url
        match_re = re.match(".*?(\d+)",response.url)
        if match_re:
            # 使用重载后的IitemLoader===>在itmes自定义t1ItemLoader
            t1 = t1ItemLoader(item=t1Item(),response=response)
            t1.add_css("title","#news_title a::text")
            t1.add_css("create_date","#news_info .time::text")
            post_id = match_re.group(1)
            t1.add_css("content","#news_content")
            t1.add_css("tags","#news_more_info .catalink::text")
            t1.add_value("url",response.url)
            t1.add_value("url_object_id",get_md5(response.url))
            # title= response.css('#news_title a::text').extract_first("")
            # create_date = response.css('#news_info .time::text').extract_first("")
            # match_re = re.match(".*?(\d+.*)",create_date)
            # if match_re:
            #     create_date = match_re.group(1)
            # content = response.css('#news_content').extract_first("")
            # tag_list = response.css('#news_more_info .catalink::text').extract()
            # tags = ",".join(tag_list)
            # t1_item["title"] = title
            # t1_item["create_date"] = create_date
            # t1_item["content"] = content
            # t1_item["tags"] = tags
            # t1_item["url"] = response.url
            if response.meta.get("front_image_url",""):
                t1.add_value("front_image_url",[response.meta.get("front_image_url","")])
                # t1_item["front_image_url"] = [response.meta.get("front_image_url","")]
            else:
                t1.add_value("front_image_url",[])
                # t1_item["front_image_url"] = []

            yield scrapy.Request(url=parse.urljoin(response.url,'/NewsAjax/GetAjaxNewsInfo?contentId={}'.format(post_id)),meta={"t1":t1},callback=self.parse_nums)



    def parse_nums(self,response):
        j_data = json.loads(response.text)
        t1 = response.meta.get("t1","")
        t1.add_value("diggcount",j_data["DiggCount"])
        t1.add_value("totalview",j_data["TotalView"])
        t1.add_value("commentcount",j_data["CommentCount"])
        t1.add_value("burycount",j_data["BuryCount"])
        # t1_item["praise_nums"] = j_data["DiggCount"]
        # t1_item["fav_nums"] = j_data["TotalView"]
        # t1_item["comment_nums"] = j_data["CommentCount"]
        # t1_item["url_object_id"] = common.get_md5(t1_item["url"])

        return t1.load_item()
