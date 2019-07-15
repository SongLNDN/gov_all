#!/usr/bin/env python 
# coding: utf-8 
"""
@author: TongYao
@file:   bjSpider.py
@time:  2019-04-29 
@function:  北京政府网新闻爬虫
"""
import re
import sys
import scrapy
from gov_all.items import GovAllItem
from gov_all.spiders.util import spiderUtil


class bjNews(scrapy.Spider):
    name = "bjSpider"
    start_url = ["http://www.beijing.gov.cn/ywdt/zybwdt/",
                 "http://www.beijing.gov.cn/ywdt/yaowen/",
                 "http://www.beijing.gov.cn/ywdt/gqrd/",
                 "http://www.beijing.gov.cn/ywdt/gzdt/"]

    header = spiderUtil.header_util()

    def start_requests(self):
        for url in self.start_url:
            # time.sleep(random.uniform(3, 5))
            yield scrapy.Request(url=url, callback=self.parse_item_page_home, headers=self.header)

    def parse_item_page_home(self, response):
        yield scrapy.Request(url=response.url, callback=self.parse_item_page_list, headers=self.header,
                             dont_filter=True)
        # max_page = response.text.split("pageCount = ")[1][:4].split(";")[0]
        # for page in range(1, int(max_page)):
        #     news_list_url = response.url+"default_" + str(page)+".htm"
        #     # time.sleep(random.uniform(3, 5))
        #     yield scrapy.Request(url=news_list_url, callback=self.parse_item_page_list, headers=self.header)

    def parse_item_page_list(self, response):
        news_list = response.xpath("//li[@class='col-md']/a/@href").extract()
        for news_url in news_list:
            if news_url.startswith("http"):
                # time.sleep(random.uniform(3, 5))
                yield scrapy.Request(url=news_url, callback=self.parse, headers=self.header)
            elif news_url.startswith("../../"):
                news_url = "http://www.beijing.gov.cn/" + news_url.replace("../../", "")
                yield scrapy.Request(url=news_url, callback=self.parse, headers=self.header)
            elif news_url.startswith("../"):
                news_url = "/".join(response.url.split("/")[:-2]) + news_url.replace("../", "/")
                yield scrapy.Request(url=news_url, callback=self.parse, headers=self.header)
            elif news_url.startswith("./"):
                news_url = "/".join(response.url.split("/")[:-1]) + news_url.replace("./", "/")
                yield scrapy.Request(url=news_url, callback=self.parse, headers=self.header)

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)

            try:
                # title = response.xpath("//head/title/text()").extract()[0].split("-")[0]
                title_arr = response.xpath("//div[@class='header']/p/text()").extract()
                title = "".join(title_arr).strip()
            except:
                spiderUtil.log_level(6, response.url)

            try:
                author_arr = response.xpath("//p[@class='fl']/span/text()").extract()
                author = "".join(author_arr).strip()
                if author == "":
                    author = "北京市人民政府"
                else:
                    author = author.split("来源：")[1]
            except:
                spiderUtil.log_level(9, response.url)

            try:
                public_time = re.search(r"(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2})", response.text).group(0) + ":00"
            except:
                spiderUtil.log_level(8, response.url)

            try:
                content_arr = response.xpath("//div[@class='TRS_Editor']/p/text()").extract()
                content = "".join(content_arr)
            except:
                spiderUtil.log_level(7, response.url)

            source = "http://www.beijing.gov.cn/"

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
