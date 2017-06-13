# -*- coding: utf-8 -*-

from datetime import datetime
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from article_crawl.items import LagouJobItem, CustomItemLoader


class LagouSpider(CrawlSpider):
    name = 'lagou'
    allowed_domains = ['www.lagou.com']
    # start_urls = ['http://www.lagou.com/']
    start_urls = ['http://www.lagou.com']

    rules = (
        # Rule(LinkExtractor(allow=r'zhaopin/.*\.html', deny=r'forbidden/fb.html.*')),
        Rule(LinkExtractor(allow=r'jobs/\d+\.html', deny=r'forbidden/fb.html.*'), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        item_loader = CustomItemLoader(item=LagouJobItem(), response=response)

        item_loader.add_value('job_id',response.url)
        item_loader.add_value('url', response.url)
        item_loader.add_xpath('position', '//div[@class="job-name"]/@title')
        # item_loader.add_xpath('lowest_salary', '//span[@class="salary"]/text()')
        # item_loader.add_xpath('highest_salary', '//span[@class="salary"]/text()')
        job_request = response.xpath('//dd[@class="job_request"]/p/span/text()').extract()
        item_loader.add_value('lowest_salary', job_request[0])
        item_loader.add_value('highest_salary', job_request[0])
        item_loader.add_value('city', job_request[1])
        item_loader.add_value('experience', job_request[2])
        item_loader.add_value('degree', job_request[3])
        item_loader.add_value('job_type', job_request[4])
        item_loader.add_xpath('publish_time', '//p[@class="publish_time"]/text()')
        item_loader.add_xpath('job_advantage', '//dd[@class="job-advantage"]/p/text()')
        item_loader.add_xpath('job_describe', '//dd[@class="job_bt"]//div//text()')
        item_loader.add_xpath('job_status','//div[@class="resume-deliver"]/a[@rel="nofollow"]/text()')
        item_loader.add_xpath('job_address', '//div[@class="work_addr"]/text()|//div[@class="work_addr"]//a/text()')
        item_loader.add_xpath('company','//dl[@id="job_company"]//img/@alt')
        item_loader.add_xpath('company_url', '//dl[@id="job_company"]/dt/a/@href')
        item_loader.add_value('crawl_time', datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S'))

        lagou_item = item_loader.load_item()
        return lagou_item

