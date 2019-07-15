#!/usr/bin/env python 
# coding: utf-8 
"""
@author: TongYao
@file:   tjSpider.py
@time:  2019-04-28 
@function:  天津市政府网站新闻
"""
import re
import time
import random
import scrapy
import sys
from gov_all.items import GovAllItem
from gov_all.spiders.util import spiderUtil


class nxNews(scrapy.Spider):
    name = "tjSpider"
    start_url = ["http://www.tj.gov.cn/xw/xwfbh/",
                 "http://www.tj.gov.cn/xw/tztg/",
                 "http://www.tj.gov.cn/xw/bum/",
                 "http://www.tj.gov.cn/xw/qx1/",
                 "http://www.tj.gov.cn/xw/bdyw/"]

    header = spiderUtil.header_util()

    def start_requests(self):
        for url in self.start_url:
            # time.sleep(random.uniform(2, 3))
            yield scrapy.Request(url=url, callback=self.parse_item_page_list, headers=self.header)

    # def parse_item_page_home(self, response):
    #     yield scrapy.Request(url=response.url, callback=self.parse_item_page_list, headers=self.header, dont_filter=True)
        # max_page = response.text.split("countPage = ")[1][:3].split("/")[0]
        # for page in range(2, int(max_page)):
        #     news_list_url = response.url+"index_" + str(page)+".html"
        #     time.sleep(1)
        #     yield scrapy.Request(url=news_list_url, callback=self.parse_item_page_list, headers=self.header)

    def parse_item_page_list(self, response):
        news_list = response.xpath("//div/div/ul/li/a/@href").extract()
        for news_url in news_list:
            if news_url.startswith("./"):
                news_url=response.url.split("/index")[0]+news_url[2:]
                time.sleep(1)
                yield scrapy.Request(url=news_url, callback=self.parse, headers=self.header)
            elif news_url.startswith("http"):
                # time.sleep(random.uniform(1, 3))
                yield scrapy.Request(url=news_url, callback=self.parse, headers=self.header)

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)

            try:
                title = response.xpath("//div[@class='title']/text()").extract()[0].strip()+response.xpath("//div[@class='t_title']/text()").extract()[0].strip()
            except:
                spiderUtil.log_level(6, response.url)

            try:
                author = response.xpath("//span[@class='ly']/text()").extract()[0].split("来源：")[1]
                if author == "":
                    author = "天津市人民政府"
            except:
                spiderUtil.log_level(9, response.url)

            try:
                public_time = re.search(r"(\d{4}-\d{1,2}-\d{1,2}\s\s\d{1,2}:\d{1,2})", response.text).group(0).replace("  "," ")+":00"
            except:
                spiderUtil.log_level(8, response.url)

            try:
                content_arr = response.xpath("//div[@class='TRS_Editor']/p/text()").extract()
                content = "".join(content_arr)
            except:
                spiderUtil.log_level(7, response.url)

            source = "http://www.tj.gov.cn/"

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
