#!/usr/bin/env python 
# coding: utf-8 
"""
@author: TongYao
@file:   xinjiangSpider.py
@time:  2019-04-25 
@function:  新疆政府网站新闻
"""
import random
import re
import time
import scrapy
import sys
from gov_all.items import GovAllItem
from gov_all.spiders.util import spiderUtil


class xinjiangNews(scrapy.Spider):
    name = "xinjiangSpider"
    start_url = ["http://www.xinjiang.gov.cn/xxgk/qwfb/zwdt/xwtt/index.html",
                 "http://www.xinjiang.gov.cn/xxgk/qwfb/zwdt/zwyw/index.html",
                 "http://www.xinjiang.gov.cn/xxgk/qwfb/zwdt/bmyw/index.html",
                 "http://www.xinjiang.gov.cn/xxgk/qwfb/zwdt/dzyw/index.html"]

    def start_requests(self):
        for url in self.start_url:
            yield scrapy.Request(url=url, callback=self.parse_item_page_list)

    def parse_item_page_list(self, response):
        news_url_list = response.xpath("//div[@class='wenz_list']/div[@class='list']/ul/li/a/@href").extract()
        for news_url in news_url_list:
            if news_url.startswith("/"):
                news_url = "http://www.xinjiang.gov.cn" + news_url
                time.sleep(random.uniform(1, 3))
                yield scrapy.Request(url=news_url, callback=self.parse,dont_filter=True)
        # next_list = response.xpath("//li/a[@class='next']/@href").extract()
        # if next_list != []:
        #     next_list = response.url.split("index")[0] + next_list[0]
        #     yield scrapy.Request(url=next_list, callback=self.parse_item_page_list)

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)
            try:
                title = response.xpath("//div[@class='title']/h1/text()").extract()[0]
            except:
                spiderUtil.log_level(6, response.url)
            try:
                author = response.xpath("//div[@class='t_left']/span/text()").extract()[1].split("来源：")[1]
                if author == "":
                    author = "新疆维吾尔人民政府"
            except:
                spiderUtil.log_level(9, response.url)

            try:
                public_time = re.search(r"(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2})", response.text).group(0)
            except:
                spiderUtil.log_level(8, response.url)

            try:
                content_arr = response.xpath("//div[@id='news_content']")[0].xpath('string(.)').extract()
                content = "".join(content_arr)
            except:
                spiderUtil.log_level(7, response.url)

            source = "http://www.xinjiang.gov.cn/"

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
            spiderUtil.log_level(response.status, response.url)
