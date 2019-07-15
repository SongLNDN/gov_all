#!/usr/bin/env python 
# coding: utf-8 
"""
@author: TongYao
@file:   qhSpider.py
@time:  2019-04-30 
@function:  青海省政府新闻爬虫
"""
import random
import re
import sys
import time

import scrapy
from gov_all.items import GovAllItem
from gov_all.spiders.util import spiderUtil


class qhNews(scrapy.Spider):
    name = "qhSpider"
    start_url = ["http://www.qh.gov.cn/zwgk/xwdt/qhyw/",
                 "http://www.qh.gov.cn/zwgk/xwdt/bmdt/",
                 "http://www.qh.gov.cn/zwgk/xwdt/dqdt/",
                 "http://www.qh.gov.cn/zwgk/xwdt/jqgz/",
                 "http://www.qh.gov.cn/zwgk/xwdt/tzgg/"]

    header = spiderUtil.header_util()

    def start_requests(self):
        for url in self.start_url:
            # time.sleep(random.uniform(3, 5))
            yield scrapy.Request(url=url, callback=self.parse_item_page_list, headers=self.header)

    def parse_item_page_list(self, response):
        news_list = response.xpath("//div[@class='box11 tabs topline']/div/ul/p[@class='item']/a/@href").extract()
        for news_url in news_list:
            time.sleep(random.uniform(1, 3))
            yield scrapy.Request(url=news_url, callback=self.parse, headers=self.header)
        # if "下一页" in response.xpath("//div[@class='pages']/a/text()").extract():
        #     next_list = response.xpath("//div[@class='pages']/a/@href").extract()
        #     next_list=next_list[len(next_list)-1]
        #     yield scrapy.Request(url=next_list, callback=self.parse_item_page_list, headers=self.header)

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)

            try:
                title_arr = response.xpath("//h1[@class='blue tc']/text()").extract()
                title = "".join(title_arr).strip()
            except:
                spiderUtil.log_level(6, response.url)

            try:
                author_arr = response.xpath("//div[@class='abstract tc']/text()").extract()
                author = "".join(author_arr).strip()
                if author == "":
                    author = "青海省人民政府"
                else:
                    author = author.split("来源：")[1].split("发布时间")[0]
            except:
                spiderUtil.log_level(9, response.url)

            try:
                public_time = re.search(r"(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2})", response.text).group(0)+":00"
            except:
                spiderUtil.log_level(8, response.url)

            try:
                content_arr = response.xpath("//div[@class='details_content']/p//text()").extract()
                content = "".join(content_arr)
            except:
                spiderUtil.log_level(7, response.url)

            source = "http://www.qh.gov.cn/"

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