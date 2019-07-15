#!/usr/bin/env python 
# coding: utf-8 
"""
@author: TongYao
@file:   xizangSpider.py
@time:  2019-04-25 
@function: 西藏政府网站新闻爬虫
"""
import re
import time
import random
import scrapy
import sys
from gov_all.items import GovAllItem
from gov_all.spiders.util import spiderUtil


class xizangNews(scrapy.Spider):
    name = "xizangSpider"
    start_url = ["http://www.xizang.gov.cn/xwzx/zwyw/",
                 "http://www.xizang.gov.cn/xwzx/jjjs/",
                 "http://www.xizang.gov.cn/xwzx/qnyw/",
                 "http://www.xizang.gov.cn/xwzx/dsyw/",
                 "http://www.xizang.gov.cn/xwzx/xqxw/",
                 "http://www.xizang.gov.cn/xwzx/xwrp/",
                 "http://www.xizang.gov.cn/xwzx/dwjl/",
                 "http://www.xizang.gov.cn/xwzx/shfz/"]

    header = spiderUtil.header_util()

    def start_requests(self):
        for url in self.start_url:
            # time.sleep(random.uniform(4,5))
            yield scrapy.Request(url=url, callback=self.parse_item_page_home)

    def parse_item_page_home(self, response):
        # text = response.text
        # max_page = text.split("createPageHTML(")[2].split(",")[0]
        # for page in range(1, int(max_page) + 1):
        # for page in range(1, 2):
            url = response.url + "index" + ".html"
            # time.sleep(random.uniform(4,5))
            yield scrapy.Request(url=url, callback=self.parse_item_page_list)

    def parse_item_page_list(self, response):
        news_list = response.xpath("//div[@class='zx-wdsyw-con']/ul/li/a/@href").extract()
        for news_url in news_list:
            if news_url.startswith("./"):
                news_url = response.url.split("/index")[0] + news_url[1:]
                # time.sleep(random.uniform(4,5))
                yield scrapy.Request(url=news_url, callback=self.parse)
            else:
                # time.sleep(random.uniform(4,5))
                yield scrapy.Request(url=news_url, callback=self.parse)

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)
            try:
                title = response.xpath("//div[@class='xz-xl-tit']/h3/text()").extract()[0].strip()
            except:
                spiderUtil.log_level(6, response.url)
            try:
                author = response.xpath("//div[@class='xz-xl-info']/p/span/text()").extract()
                if len(author)==2:
                    author=author[1]
                else:
                    author = "西藏自治区人民政府"
            except:
                spiderUtil.log_level(9, response.url)

            try:
                public_time = re.search(r"(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2})", response.text).group(0)
            except:
                spiderUtil.log_level(8, response.url)

            try:
                content_arr = response.xpath("//div[@class='xz-xl-article']")[0].xpath("string(.)").extract()
                content = "".join(content_arr).split("//显示下载附件")[0][:-106].strip()
            except:
                spiderUtil.log_level(7, response.url)

            source = "http://www.xizang.gov.cn/"

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
