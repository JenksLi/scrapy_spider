# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from fake_useragent import UserAgent
from selenium import webdriver
# from article_crawl.tools.craw_xici_ip import Get_proxy_ip


class ArticleCrawlSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class RandomUserAgentProxyIP(object):
    def __init__(self, crawler):
        self.ua = UserAgent()
        self.ua_type = crawler.settings.get('User_Agent_type', 'random')

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_request(self, request, spider):
        def get_ua():
            return getattr(self.ua, self.ua_type)
        request.headers.setdefault(b'User-Agent', get_ua())


# class ProxyIPMiddleware(object):
#     def process_request(self, request, spider):
#         get_proxy = Get_proxy_ip()
#         proxyIp = get_proxy.get_rand_ip('http')
#         request.meta['proxy'] = '{}://{}:{}'.format(proxyIp[-1], proxyIp[0], proxyIp[1])


# from scrapy.http import HtmlResponse
# # 需要解析JS的页面调用 selenium
# class JSPageMiddleware(object):
#     def __init__(self):
#         self.broswer = webdriver.Chrome()
#
#     def process_request(self, request, spider):
#         if spider.name == 'jobbole':
#             self.broswer.get(request.url)
#             print('current url: {}'.format(request.url))
#
#         return HtmlResponse(url=self.broswer.current_url, request=request, body=self.broswer.source_page, encoding='utf8')
