#!/usr/bin/env python 
# coding: utf-8 
"""
@author: TongYao
@file:   gdSpider.py
@time:  2019-04-30 
@function:  广东省政府新闻爬虫
"""
import re
import scrapy
import sys
from gov_all.items import GovAllItem
from gov_all.spiders.util import spiderUtil


class gdNews(scrapy.Spider):
    name = "gdSpider"
    start_url = ["http://www.gd.gov.cn/gdywdt/gdyw/index.html",
                 "http://www.gd.gov.cn/gdywdt/dczl/jcbs/index.html",
                 "http://www.gd.gov.cn/gdywdt/dczl/gcls/index.html",
                 "http://www.gd.gov.cn/gdywdt/dczl/dcxd/index.html",
                 "http://www.gd.gov.cn/gdywdt/bmdt/index.html",
                 "http://www.gd.gov.cn/gdywdt/dsdt/index.html",
                 "http://www.gd.gov.cn/gdywdt/zfjg/index.html",
                 "http://www.gd.gov.cn/gdywdt/tzdt/index.html",
                 "http://www.gd.gov.cn/gdywdt/ydylygd/index.html"]

    header = spiderUtil.header_util()

    def start_requests(self):
        for url in self.start_url:
            # time.sleep(random.uniform(3, 5))
            yield scrapy.Request(url=url, callback=self.parse_item_page_home, headers=self.header)

    def parse_item_page_home(self, response):
        yield scrapy.Request(url=response.url, callback=self.parse_item_page_list, headers=self.header, dont_filter=True)
        # max_page = response.xpath("//a[@class='last']/@href").extract()[0].split("index_")[1].split(".")[0]
        # for page in range(2, int(max_page)+1):
        #     news_list_url = response.url.replace("index","index_" + str(page))
        #     # time.sleep(random.uniform(3, 5))
        #     yield scrapy.Request(url=news_list_url, callback=self.parse_item_page_list, headers=self.header)

    def parse_item_page_list(self, response):
        news_list = response.xpath("//span[@class='til']/a/@href").extract()
        for news_url in news_list:
            # time.sleep(random.uniform(3, 5))
            if news_url.startswith("http://www.gd.gov.cn"):
                yield scrapy.Request(url=news_url, callback=self.parse, headers=self.header)

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)

            try:
                title = response.xpath("//h3[@class='zw-title']/text()").extract()[0].strip()
            except:
                spiderUtil.log_level(6, response.url)

            try:
                author = response.xpath("//span[@class='ly']/text()").extract()[0].split("来源  :")[1].strip()
                if author == "":
                    author = "广东省人民政府"
            except:
                spiderUtil.log_level(9, response.url)

            try:
                public_time = re.search(r"(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2})", response.text).group(0)
            except:
                spiderUtil.log_level(8, response.url)

            try:
                content_arr = response.xpath("//div[@class='zw']/p")[0].xpath('string(.)').extract()
                content = "".join(content_arr)
            except:
                spiderUtil.log_level(7, response.url)

            source = "http://www.gd.gov.cn/"

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
