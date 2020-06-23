# -*- coding: utf-8 -*-
import time
# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from fake_useragent import UserAgent
from twisted.internet.error import TimeoutError

class LagouRedisSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class LagouRedisDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        if isinstance(exception,TimeoutError):
            return request

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class RandomUserAgentMiddlware(object):
    # 随机更换user-agent
    def __init__(self,crawler):
        super(RandomUserAgentMiddlware,self).__init__()
        self.user_agent_list = crawler.settings.get("user_agent_list",[])
        self.ua = UserAgent()
        self.ua_type = crawler.settings.get("RANDOM_UA_TYPE","random")

    @classmethod
    def from_crawler(cls,crawler):
        return cls(crawler)

    def process_request(self,request,spider):
        def get_ua():
            return getattr(self.ua,self.ua_type)
        a = request.url.split("com")[1]
        request.headers.setdefault("user-agent",get_ua())
        request.headers.setdefault(":authority","www.lagou.com")
        request.headers.setdefault("cache-control","max-age=0")
        request.headers.setdefault("accept","text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9")
        request.headers.setdefault(":method","GET")
        if a != "/":
            request.headers.setdefault(":path",a)
        request.headers.setdefault("accept-encoding","gzip, deflate, br")
        request.headers.setdefault(":scheme","https")
        request.headers.setdefault("upgrade-insecure-requests",1)
        request.headers.setdefault("Connection","keep-alive")
        
    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        # print(response.text)
        return response


class RandomProxyMiddleware():
        # 动态设置ip代理
        def process_request(self,request,spider):
            proxy_url = "http://d.jghttp.golangapi.com/getip?num=200&type=2&pro=0&city=0&yys=0&port=11&pack=23746&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions="
            time.sleep(3)
            getproxy = GetProxy(proxy_url)
            proxyiter = getproxy.getip()[0]
            ip,port = proxyiter["ip"],str(proxyiter["port"])
            request.meta["proxy"] = "https://{0}:{1}".format(ip,port)

        def process_exception(self, request, exception, spider):
            # Called when a download handler or a process_request()
            # (from other downloader middleware) raises an exception.

            # Must either:
            # - return None: continue processing this exception
            # - return a Response object: stops process_exception() chain
            # - return a Request object: stops process_exception() chain
            if isinstance(exception,TimeoutError):
                print("======================================================")
                return request            
