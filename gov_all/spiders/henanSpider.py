#!/usr/bin/env python 
# encoding: utf-8 


"""
 Created by songyao@mail.ustc.edu.cn on 2019/4/30 下午1:52
 
 Function: 河南省 人民政府   http://www.henan.gov.cn/ywdt/hnyw/  测试通过
 
"""
import re

import scrapy
import sys
from gov_all.spiders.util import spiderUtil
from gov_all.items import GovAllItem
import time
import random

class moNews(scrapy.Spider):
    name = "henanSpider"
    start_url = "http://www.henan.gov.cn/ywdt/hnyw/"
    header = spiderUtil.header_util()

    def start_requests(self):
        yield scrapy.Request(url="http://www.henan.gov.cn/ywdt/hnyw/", callback=self.parse_item_page_list, headers=self.header)

    def parse_item_page_list(self, response):
        detail_urls = response.xpath("//div[@class='main']//li/a/@href").extract()
        for detail_url in detail_urls:
            time.sleep(random.uniform(1, 3))
            print(detail_url)
            yield scrapy.Request(url=detail_url, callback=self.parse, headers=self.header)

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)
            try:
                titles = response.xpath("""//*[@id='title']//text()""").extract()
                title = "".join(titles).strip()
            except:
                spiderUtil.log_level(6, response.url)

            try:
                authors = response.xpath("""//*[@id='source']//text()""").extract()
                author = "".join(authors).strip()
            except:
                spiderUtil.log_level(9, response.url)

            try:
                public_time = re.search(r"(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2})", response.text).group(0)+":00"
            except:
                # spiderUtil.log_level(8, response.url)
                pass
            source = "http://www.henan.gov.cn/"

            try:
                content_detail = response.xpath("""//*[@class='content']//text()""").extract()
                content = ""
                for i in range(0, len(content_detail)):
                    content = content + content_detail[i]
            except:
                spiderUtil.log_level(7, response.url)

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
                    # print(item)
                    yield item
            except:
                pass
        else:
            spiderUtil.log_level(response.status_code, response.url)



