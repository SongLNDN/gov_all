#!/usr/bin/env python 
# encoding: utf-8 


"""
 Created by songyao@mail.ustc.edu.cn on 2019/4/28 下午2:11
 
 Function:  黑龙江 测试通过
 
"""

import time
import random
import scrapy
import sys
from gov_all.items import GovAllItem
from gov_all.spiders.util import spiderUtil


class heilongjiangNews(scrapy.Spider):
    name = "heilongjiangSpider"
    start_url = ["http://www.hlj.gov.cn/"]
    header = spiderUtil.header_util()

    def start_requests(self):
        yield scrapy.Request(url="http://www.hlj.gov.cn/zwfb/zxfb/index.shtml", callback=self.parse_item_page_list,headers=self.header)
        yield scrapy.Request(url="http://www.hlj.gov.cn/szf/lddt/cxhd/", callback=self.parse_item_page_list,headers=self.header)

    def parse_item_page_list(self, response):
        detail_urls = response.xpath("//div[@class='li-left hei']//span/a/@href").extract()
        for detail_url in detail_urls:
            yield scrapy.Request(url=detail_url, callback=self.parse, headers=self.header)

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)
            try:
                title = response.xpath("""//div[@class="tm2"]/text()""").extract()[0]
            except:
                spiderUtil.log_level(6, response.url)
            try:
                authors = response.xpath("""//div[@class="tm3"]/span[2]/text()""").extract()
                author = "".join(authors).replace("来源：","").strip()
                if author=="":
                    author="黑龙江人民政府网"
            except:
                spiderUtil.log_level(9, response.url)

            try:
                public_times = response.xpath("""//div[@class="tm3"]/span[1]/text()""").extract()
                public_time = "".join(public_times).replace("时间：", "").strip()
            except:
                spiderUtil.log_level(8, response.url)

            try:
                content_arr = response.xpath("//div[@class='nr5']/p/text()").extract()
                content = "".join(content_arr)
            except:
                spiderUtil.log_level(7, response.url)

            source = "http://www.hlj.gov.cn/"

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
            spiderUtil.log_level(response.status, response.url)



