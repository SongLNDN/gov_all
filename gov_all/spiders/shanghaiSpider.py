#!/usr/bin/env python 
# coding: utf-8 
"""
@author: TongYao
@file:   shanghaiSpider.py
@time:  2019-04-29 
@function: 上海政府网站新闻爬虫
"""
import re
import time
import random
import scrapy
import sys
from gov_all.items import GovAllItem
from gov_all.spiders.util import spiderUtil


class shanghaiNews(scrapy.Spider):
    name = "shanghaiSpider"
    start_url = ["http://www.shanghai.gov.cn/nw2/nw2314/nw2315/nw4411/index.html",
                 "http://www.shanghai.gov.cn/nw2/nw2314/nw2315/nw18454/index.html",
                 "http://www.shanghai.gov.cn/nw2/nw2314/nw2315/nw15343/index.html",
                 "http://www.shanghai.gov.cn/nw2/nw2314/nw2315/nw31406/index.html"]

    header = spiderUtil.header_util()

    def start_requests(self):
        for url in self.start_url:
            # time.sleep(random.uniform(3, 5))
            yield scrapy.Request(url=url, callback=self.parse_item_page_list, headers=self.header)

    def parse_item_page_list(self, response):
        news_list = response.xpath("//ul[@class='uli14 pageList']/li/a/@href").extract()
        for news_url in news_list:
            news_url="http://www.shanghai.gov.cn"+news_url
            # time.sleep(random.uniform(3, 5))
            yield scrapy.Request(url=news_url, callback=self.parse, headers=self.header)
        # next_page = response.xpath("//li/a[@class='action']/@href").extract()
        # if next_page!=[]:
        #     next_url="http://www.shanghai.gov.cn"+next_page[0]
        #     # time.sleep(random.uniform(3, 5))
        #     yield scrapy.Request(url=next_url, callback=self.parse_item_page_list, headers=self.header)

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)
            try:
                title = response.xpath("//div[@id='ivs_title']/text()").extract()[0].strip()
            except:
                spiderUtil.log_level(6, response.url)
            try:
                author = response.xpath("//small[@class='PBtime']/text()").extract()[0].split("来源：")[1]
                if author == "":
                    author = "上海市人民政府"
            except:
                spiderUtil.log_level(9, response.url)

            try:
                public_time = re.search(r"(\d{4}年\d{1,2}月\d{1,2}日\s\s\s\d{1,2}\s:\s\d{1,2})", response.text).group(0).replace("年","-").replace("月","-").replace("日","").replace("   "," ").replace(" : ",":")+":00"
            except:
                spiderUtil.log_level(8, response.url)

            try:
                content_arr = response.xpath("//div[@id='ivs_content']")[0].xpath('string(.)').extract()
                content = "".join(content_arr)
            except:
                spiderUtil.log_level(7, response.url)

            source = "http://www.shanghai.gov.cn/"

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