#!/usr/bin/env python 
# coding: utf-8 
"""
@author: TongYao
@file:   moSpider.py
@time:  2019-04-23 
@function:  澳门政府网站新闻爬虫
"""
import re
import scrapy
import sys
from gov_all.spiders.util import spiderUtil
from gov_all.items import GovAllItem


class moNews(scrapy.Spider):
    name = "moSpider"
    start_url = "https://www.gov.mo/zh-hant/%s/%s/page/%s/?post_type=news_post"
    header = spiderUtil.header_util()

    def start_requests(self):
        # date_set = set()
        # begin_date = datetime.datetime.strptime("2017-09-01", "%Y-%m-%d")
        # end_date = datetime.datetime.strptime(time.strftime('%Y-%m-%d', time.localtime(time.time())), "%Y-%m-%d")
        # while begin_date <= end_date:
        #     date_str = begin_date.strftime("%Y-%m")
        #     date_set.add(date_str)
        #     begin_date += datetime.timedelta(days=1)
        # date_list = list(date_set)
        # date_list.sort()
        #
        # for date in date_list:
        #     today = date.split("-")
        today = spiderUtil.get_time().split("-")
        year = today[0]
        month = today[1]
        for page in range(1, 3):
            url = self.start_url % (year, month, page)
            yield scrapy.Request(url=url, callback=self.parse_item_page_list, headers=self.header)

    def parse_item_page_list(self, response):
        # news_url_list = response.xpath("//h2/a/@href").extract()
        news_url_list = response.xpath("//div[@class='card-head news--item-head style-primary']/a/@href").extract()
        for news_url in news_url_list:
            yield scrapy.Request(url=news_url, callback=self.parse, headers=self.header)

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)
            try:
                title = response.xpath("//head/title/text()").extract()[0].split("–")[0].strip()
            except:
                spiderUtil.log_level(6, response.url)

            try:
                author = response.xpath("//dl/dd")[0].xpath('string(.)').extract()[0]
            except:
                spiderUtil.log_level(9, response.url)

            try:
                public_time = re.search(r"(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2})", response.text).group(0)
            except:
                spiderUtil.log_level(8, response.url)

            source = "https://www.gov.mo/"

            try:
                content_arr = response.xpath("//article/p/text()").extract()
                content = "".join(content_arr)
            except:
                spiderUtil.log_level(7, response.url)

            try:
                if len(content) > 50 and (public_time.startswith(spiderUtil.get_first_hour()) or public_time.startswith(
                        spiderUtil.get_first_twohour()) or public_time.startswith(spiderUtil.get_first_threehour())):
                    item = GovAllItem()
                    item["source"] = source
                    item["content"] = content
                    item["public_time"] = public_time
                    item["url"] = response.url
                    item["title"] = title
                    item["author"] = author
                    item["crawl_time"] = spiderUtil.get_time()
                    item["html_size"] = html_size
                    # 数据打入piplines处理
                    # print(item)
                    yield item
            except:
                pass
        else:
            spiderUtil.log_level(response.status_code, response.url)
