#!/usr/bin/env python 
# coding: utf-8 
"""
@author: TongYao
@file:   cqSpider.py
@time:  2019-04-29 
@function:    重庆政府网站新闻爬虫
"""
import re
import time
import random
import scrapy
import sys
from gov_all.items import GovAllItem
from gov_all.spiders.util import spiderUtil


class cqNews(scrapy.Spider):
    name = "cqSpider"
    start_url = ["http://www.cq.gov.cn/zqfz/whly",
                 "http://www.cq.gov.cn/zqfz/sthj",
                 "http://www.cq.gov.cn/zqfz/shfz",
                 "http://www.cq.gov.cn/zqfz/gmjj",
                 "http://www.cq.gov.cn/zwxx/jrcq",
                 "http://www.cq.gov.cn/zwxx/zwdt"]

    header = spiderUtil.header_util()

    def start_requests(self):
        for url in self.start_url:
            # for page in range(1,473):
            for page in range(1, 2):
                # time.sleep(random.uniform(2, 3))
                yield scrapy.Request(url=url + "_" + str(page), callback=self.parse_item_page_list, headers=self.header,
                                     dont_filter=True)

    def parse_item_page_home(self, response):
        print("=====" * 40)
        print(response.text)
        # max_page = response.xpath("//span[@class='total']/text()").extract()[0].split("/")[1][1:-1]
        # for page in range(1, int(max_page) + 1):
        #     url = response.url + "_" + str(page)
        #     time.sleep(random.uniform(2, 3))
        #     yield scrapy.Request(url=url, callback=self.parse_item_page_list, headers=self.header,dont_filter=True)

    def parse_item_page_list(self, response):
        print(response.text)
        print("="*100)
        news_list = response.xpath("//ul[@class='list']/li/a/@href").extract()
        for news_url in news_list:
            news_url = "http://www.cq.gov.cn" + news_url
            time.sleep(random.uniform(1, 3))
            yield scrapy.Request(url=news_url, callback=self.parse, headers=self.header)

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)
            try:
                title_arr = response.xpath("//h2[@class='title']/text()").extract()
                title = "".join(title_arr).strip()
            except:
                spiderUtil.log_level(6, response.url)
            try:
                author_arr = response.xpath("//span[@class='fl']/span/text()").extract()
                author = "".join(author_arr).strip()
                if author == "":
                    author = "重庆市人民政府"
                else:
                    author = author.split("来源：")[1]
            except:
                spiderUtil.log_level(9, response.url)

            try:
                public_time = re.search(r"(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2})", response.text).group(0) + ":00"
            except:
                spiderUtil.log_level(8, response.url)

            try:
                content_arr = response.xpath("//div[@class='conTxt']")[0].xpath('string(.)').extract()
                content = "".join(content_arr).split("终审 ：")[0].strip()
            except:
                spiderUtil.log_level(7, response.url)

            source = "http://www.cq.gov.cn/"

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
