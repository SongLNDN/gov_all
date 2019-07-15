#!/usr/bin/env python 
# coding: utf-8 
"""
@author: TongYao
@file:   sxSpider.py
@time:  2019-04-30 
@function:  陕西省政府新闻爬虫
"""
import re
import sys
import scrapy
from gov_all.items import GovAllItem
from gov_all.spiders.util import spiderUtil


class sxNews(scrapy.Spider):
    name = "sxSpider"
    start_url = ["http://www.shaanxi.gov.cn/info/iList.jsp?cat_id=10001",
                 "http://www.shaanxi.gov.cn/info/iList.jsp?cat_id=10003",
                 "http://www.shaanxi.gov.cn/info/iList.jsp?cat_id=10002",
                 "http://www.shaanxi.gov.cn/info/iList.jsp?cat_id=17469"]

    header = spiderUtil.header_util()

    def start_requests(self):
        for url in self.start_url:
            # time.sleep(random.uniform(3, 5))
            yield scrapy.Request(url=url, callback=self.parse_item_page_list, headers=self.header)

    def parse_item_page_list(self, response):
        news_list = response.xpath("//ul[@class='xwlist-ul']/li/a/@href").extract()
        for news_url in news_list:
            news_url="http://www.shaanxi.gov.cn"+news_url
            yield scrapy.Request(url=news_url, callback=self.parse, headers=self.header)
        # next_list = response.xpath("//form/span/a/@href").extract()
        # next_list=response.url.split("?")[0]+next_list[-2]
        # yield scrapy.Request(url=next_list, callback=self.parse_item_page_list, headers=self.header)

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)

            try:
                title = response.xpath("//h1[@class='news_h1']/text()").extract()[0].strip()
            except:
                spiderUtil.log_level(6, response.url)

            try:
                author = response.xpath("//span[@id='info_source']/text()").extract()[0].strip()
                if author == "":
                    author = "陕西省人民政府"
            except:
                spiderUtil.log_level(9, response.url)

            try:
                public_time = re.search(r"(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2})", response.text).group(0)
            except:
                spiderUtil.log_level(8, response.url)

            try:
                content_arr = response.xpath("//div[@id='info-cont']/p/text()").extract()
                content = "".join(content_arr)
            except:
                spiderUtil.log_level(7, response.url)

            source = "http://www.shanxi.gov.cn/"

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