#!/usr/bin/env python 
# coding: utf-8 
"""
@author: TongYao
@file:   nmgSpider.py
@time:  2019-04-23
@function: 内蒙古政府网站新闻爬虫
"""
import re
import time
import random
import scrapy
from lxml import etree
import sys
from gov_all.items import GovAllItem
from gov_all.spiders.util import spiderUtil


class nmgNews(scrapy.Spider):
    name = "nmgSpider"
    start_url = ["http://www.nmg.gov.cn/col/col442/index.html",
                 "http://www.nmg.gov.cn/col/col443/index.html",
                 "http://www.nmg.gov.cn/col/col1141/index.html",
                 "http://www.nmg.gov.cn/col/col1972/index.html",
                 "http://www.nmg.gov.cn/col/col1973/index.html",
                 "http://www.nmg.gov.cn/col/col365/index.html",
                 "http://www.nmg.gov.cn/col/col151/index.html",
                 "http://www.nmg.gov.cn/col/col152/index.html",
                 "http://www.nmg.gov.cn/col/col360/index.html",
                 "http://www.nmg.gov.cn/col/col1253/index.html",
                 "http://www.nmg.gov.cn/col/col359/index.html",
                 "http://www.nmg.gov.cn/col/col389/index.html"
                 ]
    header = spiderUtil.header_util()

    def start_requests(self):
        for url in self.start_url:
            # for page in range(1, 329):
             for page in range(1, 2):
                news_list=url + "?uid=777&pageNum=" + str(page)
                # time.sleep(random.uniform(1, 3))
                yield scrapy.Request(url=news_list, callback=self.parse_item_page_list,headers=self.header)

    def parse_item_page_list(self, response):
        s = response.xpath("//script[@type='text/xml']/text()").extract()[0]
        url_list = etree.HTML(s).xpath("//a/@href")
        for url in url_list:
            url = "http://www.nmg.gov.cn/" + url
            time.sleep(1)
            yield scrapy.Request(url=url, callback=self.parse,headers=self.header)

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)
            try:
                title = response.xpath("//div[@class='main-fl-tit']/text()").extract()
                title = "".join("".join(title).split())
            except:
                spiderUtil.log_level(6, response.url)
            try:
                author_arr = response.xpath("//div[@class='main-fl-bjxx']/div/text()").extract()
                author = "".join(author_arr).strip()
                if author=="":
                    author="内蒙古自治区人民政府网"
            except:
                spiderUtil.log_level(9, response.url)

            try:
                public_time = re.search(r"(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2})", response.text).group(0)
            except:
                spiderUtil.log_level(8, response.url)

            try:
                content_arr = response.xpath("//div[@id='zoom']")[0].xpath('string(.)').extract()
                content = "".join(content_arr)
            except:
                spiderUtil.log_level(7, response.url)

            source = "http://www.nmg.gov.cn/"

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
