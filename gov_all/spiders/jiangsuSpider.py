#!/usr/bin/env python 
# encoding: utf-8 


"""
 Created by songyao@mail.ustc.edu.cn on 2019/4/29 下午1:58
 
 Function: 江苏省人民政府  测试通过
 
"""

import time
import random
import scrapy
import sys

from lxml import etree

from gov_all.items import GovAllItem
from gov_all.spiders.util import spiderUtil


class heilongjiangNews(scrapy.Spider):
    name = "jiangsuSpider"
    start_url = "http://www.js.gov.cn/"
    header = spiderUtil.header_util()

    def start_requests(self):
        yield scrapy.Request(url="http://www.js.gov.cn/col/col60096/index.html", callback=self.parse_item_page_list,
                             headers=self.header)
        # 全量爬取历史数据
        # for i in range(2, 69):
        #     url = "http://www.js.gov.cn/col/col60096/index.html?uid=212860&pageNum=" + str(i)
        #     yield scrapy.Request(url=url, callback=self.parse_item_page_list, headers=self.header)

    def parse_item_page_list(self, response):
        s = response.xpath("//script[@type='text/xml']/text()").extract()[0]
        url_list = etree.HTML(s).xpath("""//a/@href""")
        for url in url_list:
            url = "http://www.js.gov.cn" + url
            yield scrapy.Request(url=url, callback=self.parse, headers=self.header)

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)
            try:
                title = response.xpath("""//div[@class='sp_title']/text()""").extract()[0]
            except:
                spiderUtil.log_level(6, response.url)
            try:
                authors = response.xpath("""//div[@class='sp_time']/font[2]/text()""").extract()
                author = "".join(authors).replace("来源：", "").strip()
                if author == "":
                    author = "江苏人民政府网"
            except:
                spiderUtil.log_level(9, response.url)

            try:
                public_times = response.xpath("""//div[@class='sp_time']/font[1]/text()""").extract()[0]
                public_time = str(str(public_times).replace("发布日期：", "")) + ":00"
            except:
                spiderUtil.log_level(8, response.url)

            try:
                content_arr = response.xpath("//div[@id='zoom']//text()").extract()
                content = "".join(content_arr)
            except:
                spiderUtil.log_level(7, response.url)

            source = "http://www.js.gov.cn/"

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
            spiderUtil.log_level(response.status, response.url)
