# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import re
from datetime import datetime, timedelta
import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join, Identity, Compose


def get_num(value):
    val_match = re.search(r'(^\d+)', value)
    if val_match:
        return val_match.group(1)
    return 'null'


class JobboleItem(scrapy.Item):
    article_url = scrapy.Field()
    url_object_id = scrapy.Field()  #URL转换
    cover = scrapy.Field()          #文章封面图
    cover_path = scrapy.Field()     #封面图存放路径
    title = scrapy.Field()
    time = scrapy.Field()
    content = scrapy.Field()
    tag = scrapy.Field()


class CustomItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


class ZhihuQuestionItem(scrapy.Item):
    question_id = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    topics = scrapy.Field()
    # content = scrapy.Field()
    answer_num = scrapy.Field(
        input_processor=MapCompose(get_num)
    )
    # comment_num = scrapy.Field()
    view_num = scrapy.Field()
    crawl_time = scrapy.Field()

    ##sql插入，传递到pipeline执行
    def insert_sql(self):
        sql = """INSERT INTO question VALUES ({},'{}','{}','{}',{},{},'{}',NULL)
                  ON DUPLICATE KEY UPDATE title='{}', crawl_update_time=NOW()"""
        key = ['question_id','url','topics','title','answer_num','view_num','crawl_time']
        sql = sql.format(*[self[i] for i in key], self['title'])
        return sql


class ZhihuAnswerItem(scrapy.Item):
    answer_id = scrapy.Field()
    question_id = scrapy.Field()
    url = scrapy.Field()
    author_id = scrapy.Field()
    author_name = scrapy.Field()
    content = scrapy.Field()
    vote_num = scrapy.Field()
    comment_num = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    crawl_time = scrapy.Field()

    ##sql插入，传递到pipeline执行
    def insert_sql(self):
        sql = """INSERT INTO answer VALUES ({},{},'{}','{}','{}','{}',{},{},'{}','{}','{}',NULL)
                  ON DUPLICATE KEY UPDATE author_id='{}',author_name='{}',content='{}',vote_num={},
                  comment_num={},update_time={},create_update_time=now()"""
        key = ['answer_id','question_id','url','author_id','author_name','content',
               'vote_num','comment_num','create_time','update_time','crawl_time']
        sql = sql.format(*[self[i] for i in key],self['author_id'],self['author_name'],self['content'],self['vote_num'],
                         self['comment_num'],self['update_time'])
        return sql


def lagou_time(t):
    t = re.search(r'(^[\d\-\:])',t).group(1)

    try:
        date = datetime.strptime(t, "%Y-%m-%d")
        return date
    except:
            try:
                datetime.strptime(t, "%H:%M")
                return datetime.strftime(datetime.now(), '%Y-%m-%d')
            except:
                date = datetime.strftime(datetime.now() - timedelta(days=int(t)), '%Y-%m-%d')
                return date


def lagou_addr(addr):
    if len(addr)>1:
        address = list(map(lambda x: '' if re.search(r'([\w\u4E00-\u9FA5]+)', x) is None else re.search(r'([\w\u4E00-\u9FA5]+)', x).group(1), addr))
        address = ''.join(address[:-2])
    else:
        address = addr[0]
    return address


class LagouJobItem(scrapy.Item):
    job_id = scrapy.Field(
        input_processor=MapCompose(lambda x: 'null' if re.search(r'(\d+)', x) is None else re.search(r'(\d+)', x).group(1))
    )
    url = scrapy.Field()
    position = scrapy.Field()
    lowest_salary = scrapy.Field(
        input_processor=MapCompose(lambda x: int(list(filter(lambda j: j!=None, re.search(r'^(\d+)k[\u4E00-\u9FA5]+|^(\d+)k-', x, re.I).groups()))[0])*1000)
    )
    highest_salary = scrapy.Field(
        input_processor=MapCompose(lambda x: int(list(filter(lambda j: j!=None, re.search(r'^(\d+)k[\u4E00-\u9FA5]+|-(\d+)k', x, re.I).groups()))[0])*1000)
    )
    city = scrapy.Field(
        input_processor=MapCompose(lambda x: x.strip('/'))
    )
    experience = scrapy.Field(
        input_processor=MapCompose(lambda x: x.strip('/'))
    )
    degree = scrapy.Field(
        input_processor=MapCompose(lambda x: x.strip('/'))
    )
    job_type = scrapy.Field()
    publish_time = scrapy.Field(
        input_processor=MapCompose(lagou_time)
    )
    job_advantage = scrapy.Field()
    job_describe = scrapy.Field(
        output_processor=Join()
    )
    job_address = scrapy.Field(
        # input_processor=Compose(lambda i: ''.join(list(map(lambda x: '' if re.search(r'([\w\u4E00-\u9FA5]+)', x) is None else re.search(r'([\w\u4E00-\u9FA5]+)', x).group(1), i))[:-2]))
        input_processor=Compose(lagou_addr)
    )
    job_status = scrapy.Field(
        input_processor=MapCompose(lambda x: '有效' if x == '投个简历' else x)
    )
    company = scrapy.Field()
    company_url = scrapy.Field()
    crawl_time = scrapy.Field()

    def insert_sql(self):
        sql = """INSERT INTO lagou_job VALUES({},'{}','{}',{},{},'{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}',NULL)
                  ON DUPLICATE KEY UPDATE crawl_update_time=now()"""
        key = ['job_id','url','position','lowest_salary','highest_salary','city','experience',
                'degree','job_type','publish_time','job_advantage','job_describe','job_address',
                'job_status','company','company_url','crawl_time']
        insert_sql = sql.format(*[self.get(i) for i in key])
        return insert_sql