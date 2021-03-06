#!/usr/bin/env python 
# coding: utf-8 
"""
@author: TongYao
@file:   ynSpider.py
@time:  2019-04-30 
@function:  云南省政府网站新闻爬虫
"""
import re
import sys
import scrapy
from gov_all.items import GovAllItem
from gov_all.spiders.util import spiderUtil


class ynNews(scrapy.Spider):
    name = "ynSpider"
    start_url = ["http://www.yn.gov.cn/ywdt/bmdt/",
                 "http://www.yn.gov.cn/ywdt/ynyw/",
                 "http://www.yn.gov.cn/ywdt/zsdt/"]

    header = spiderUtil.header_util()

    def start_requests(self):
        for url in self.start_url:
            # time.sleep(random.uniform(3, 5))
            yield scrapy.Request(url=url, callback=self.parse_item_page_list, headers=self.header)
            # for i in range(1,100):
            # for i in range(1,2):
            #     url =url.split("index")[0]+("index_"+str(i))+".html"
            #     yield scrapy.Request(url=url, callback=self.parse_item_page_list, headers=self.header)

    def parse_item_page_list(self, response):
        news_list = response.xpath("//dl[@class='thlist']/dt/a/@href").extract()
        for news_url in news_list:
            if news_url.startswith("./"):
                news_url=response.url.split("index")[0]+news_url[2:]
                yield scrapy.Request(url=news_url, callback=self.parse, headers=self.header)

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)

            try:
                title = response.xpath("//div[@class='articl']/h3//text()").extract()[0].strip()
            except:
                spiderUtil.log_level(6, response.url)

            try:
                author = response.xpath("//div[@class='datetime']/text()").extract()[0].split("来源：")[1].split("2")[0].strip()
                if author == "":
                    author = "云南省人民政府"
            except:
                spiderUtil.log_level(9, response.url)

            try:
                public_time = re.search(r"(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2})", response.text).group(0)
            except:
                spiderUtil.log_level(8, response.url)

            try:
                content_arr = response.xpath("//div[@class='TRS_Editor']/p/text()").extract()
                content = "".join(content_arr)
            except:
                spiderUtil.log_level(7, response.url)

            source = "http://www.yn.gov.cn/"

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
                    yield item
                    # print(item)
            except:
                pass
        else:
            spiderUtil.log_level(response.status, response.url)