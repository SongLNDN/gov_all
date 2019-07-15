#!/usr/bin/env python 
# coding: utf-8 
"""
@author: TongYao
@file:   nxSpider.py
@time:  2019-04-26 
@function:  宁夏政府网站新闻爬虫
"""
import re
import time
import random
import scrapy
import sys
from gov_all.items import GovAllItem
from gov_all.spiders.util import spiderUtil


class nxNews(scrapy.Spider):
    name = "nxSpider"
    start_url = ["http://www.nx.gov.cn/zwxx_11337/wztt/",
                 "http://www.nx.gov.cn/zwxx_11337/zwdt/",
                 "http://www.nx.gov.cn/zwxx_11337/sxdt/",
                 "http://www.nx.gov.cn/zwxx_11337/hygq/",
                 "http://www.nx.gov.cn/ztsj/zt/tpgj_1542/",
                 "http://www.nx.gov.cn/ztsj/zt/hjbhdc/",
                 "http://www.nx.gov.cn/zwxx_11337/zcjd/",
                 "http://www.nx.gov.cn/zwgk/tzgg/"]

    header = spiderUtil.header_util()

    def start_requests(self):
        for url in self.start_url:
            # time.sleep(random.uniform(3, 5))
            yield scrapy.Request(url=url, callback=self.parse_item_page_home, headers=self.header)

    def parse_item_page_home(self, response):
        # text = response.text
        # max_page = text.split("createPageHTML(")[2].split(",")[0]
        # for page in range(1, int(max_page)+1):
        # for page in range(1, 2):
            news_list_url = response.url + "index" + ".html"
            # time.sleep(random.uniform(3, 5))
            yield scrapy.Request(url=news_list_url, callback=self.parse_item_page_list, headers=self.header)

    def parse_item_page_list(self, response):
        news_list = response.xpath("//ul[@class='commonList_dot']/li/a/@href").extract()
        for news_url in news_list:
            if news_url.startswith("./"):
                news_url = response.url.split("index")[0] + news_url[2:]
            elif news_url.startswith("../"):
                news_url = "http://www.nx.gov.cn/zwxx_11337" + news_url[2:]
            # time.sleep(random.uniform(3, 5))
            yield scrapy.Request(url=news_url, callback=self.parse, headers=self.header)

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)

            try:
                title_arr = response.xpath("//div[@id='info_title']/text()").extract()
                title = "".join(title_arr).strip()
            except:
                spiderUtil.log_level(6, response.url)

            try:
                author_arr = response.xpath("//span[@id='info_source']/text()").extract()
                author = "".join(author_arr).strip()
                if author == "":
                    author = "宁夏回族自治区人民政府"
            except:
                spiderUtil.log_level(9, response.url)

            try:
                public_time = re.search(r"(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2})", response.text).group(0)
            except:
                # spiderUtil.log_level(8, response.url)
                pass

            try:
                content_arr = response.xpath("//div[@class='view TRS_UEDITOR trs_paper_default trs_word trs_key4format']/p//text()").extract()
                content = "".join(content_arr).strip()
            except:
                spiderUtil.log_level(7, response.url)

            source = "http://www.nx.gov.cn/"

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
