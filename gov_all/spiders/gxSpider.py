#!/usr/bin/env python 
# coding: utf-8 
"""
@author: TongYao
@file:   gxSpider.py
@time:  2019-04-28 
@function:  广西政府网新闻爬虫
"""
import re
import time
import random
import scrapy
import sys
from gov_all.items import GovAllItem
from gov_all.spiders.util import spiderUtil


class gxNews(scrapy.Spider):
    name = "gxSpider"
    start_url = ["http://www.gxzf.gov.cn/zwhd/index.shtml",
                 "http://www.gxzf.gov.cn/sytt/index.shtml",
                 "http://www.gxzf.gov.cn/zcjd/index.shtml",
                 "http://www.gxzf.gov.cn/gggs/index.shtml",
                 "http://www.gxzf.gov.cn/zwdc/index.shtml",
                 "http://www.gxzf.gov.cn/dflz/yw/index.shtml"]

    header = spiderUtil.header_util()

    def start_requests(self):
        for url in self.start_url:
            # time.sleep(random.uniform(3, 5))
            yield scrapy.Request(url=url, callback=self.parse_item_page_home, headers=self.header)

    def parse_item_page_home(self, response):
        yield scrapy.Request(url=response.url, callback=self.parse_item_page_list, headers=self.header, dont_filter=True)
        # max_page = response.xpath("//div[@class='more-page']/a/@href").extract()[-1].split("-")[1][:-6]
        # for page in range(2, int(max_page)+1):
        #     news_list_url = response.url.replace("index","index-" + str(page))
        #     # time.sleep(random.uniform(3, 5))
        #     yield scrapy.Request(url=news_list_url, callback=self.parse_item_page_list, headers=self.header)

    def parse_item_page_list(self, response):
        news_list = response.xpath("//ul[@class='more-list']/li/a/@href").extract()
        for news_url in news_list:
            # time.sleep(random.uniform(3, 5))
            yield scrapy.Request(url=news_url, callback=self.parse, headers=self.header)

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)

            try:
                title_arr = response.xpath("//div[@class='article']/h1/text()").extract()
                title = "".join(title_arr).strip()
            except:
                spiderUtil.log_level(6, response.url)

            try:
                author_arr = response.xpath("//div[@class='article-inf-left']/text()").extract()
                author = "".join(author_arr)
                if author == "":
                    author = "广西壮族自治区人民政府"
            except:
                spiderUtil.log_level(9, response.url)

            try:
                public_time = re.search(r"(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2})", response.text).group(0)
            except:
                spiderUtil.log_level(8, response.url)

            try:
                content_arr = response.xpath("//div[@class='article-con']/p/text()").extract()
                content = "".join(content_arr)
            except:
                spiderUtil.log_level(7, response.url)

            source = "http://www.gxzf.gov.cn/"

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
