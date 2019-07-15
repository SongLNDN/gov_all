#!/usr/bin/env python 
# encoding: utf-8 


"""
 Created by songyao@mail.ustc.edu.cn on 2019/4/29 下午1:52
 
 Function: 吉林省人民政府
 
""" 


import scrapy
import sys
from gov_all.spiders.util import spiderUtil
from gov_all.items import GovAllItem
import time
import random

class moNews(scrapy.Spider):
    name = "jilinSpider"
    start_url = "http://www.jl.gov.cn/"
    header = spiderUtil.header_util()

    def start_requests(self):
        yield scrapy.Request(url="http://www.jl.gov.cn/zw/yw/jlyw/index.html", callback=self.parse_item_page_list, headers=self.header)

    def parse_item_page_list(self, response):
        detail_urls = response.xpath("""//li[@class="item"]//a/@href""").extract()
        for detail_url in detail_urls:
            if "./" in detail_url:
                detail_url = "http://www.jl.gov.cn/zw/yw/jlyw/" + detail_url.replace("./", "")
                time.sleep(random.uniform(1, 3))
                yield scrapy.Request(url=detail_url, callback=self.parse, headers=self.header)

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)
            try:
                content_title = response.xpath("""//div[@id="dbt"]//text()""").extract()
                title = "".join(content_title).strip()
            except:
                spiderUtil.log_level(6, response.url)

            try:
                author = "吉林省人民政府"

            except:
                spiderUtil.log_level(9, response.url)

            try:
                content_time = response.xpath("""//div[@class="c_xx"]//text()""").extract()
                public_times = str(content_time[0]).split("   ")
                public_time = str(public_times[1])
            except:
                spiderUtil.log_level(8, response.url)

            source = "http://www.jl.gov.cn/"

            try:
                content_detail = response.xpath("""//div[@class='TRS_Editor']//text()""").extract()
                content = "".join(content_detail).strip()
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
                    yield item
            except:
                pass
        else:
            spiderUtil.log_level(response.status_code, response.url)

