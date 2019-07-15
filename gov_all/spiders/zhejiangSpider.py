#!/usr/bin/env python 
# encoding: utf-8 


"""
 Created by songyao@mail.ustc.edu.cn on 2019/4/29 下午2:24
 
 Function: 浙江省人民政府 http://www.zj.gov.cn/col/col1554467/index.html 测试通过
 
""" 


import scrapy
import sys

from lxml import etree

from gov_all.spiders.util import spiderUtil
from gov_all.items import GovAllItem

class moNews(scrapy.Spider):
    name = "zhejiangSpider"
    start_url = "http://www.zj.gov.cn/"
    header = spiderUtil.header_util()

    def start_requests(self):
        yield scrapy.Request(url="http://www.zj.gov.cn/col/col1554467/index.html", callback=self.parse_item_page_list, headers=self.header)

    def parse_item_page_list(self, response):
        s = response.xpath("//script[@type='text/xml']/text()").extract()[0]
        url_list = etree.HTML(s).xpath("""//a/@href""")
        for url in url_list:
            url = "http://www.zj.gov.cn" + url
            yield scrapy.Request(url=url, callback=self.parse, headers=self.header)

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)
            try:
                content_title = response.xpath("""//td[@align="center"]/text()""").extract()
                title = "".join(content_title)
            except:
                spiderUtil.log_level(6, response.url)

            try:
                authors = response.xpath("""//ul[@class="list"]/li[2]/text()""").extract()
                author = "".join(authors).replace("来源：", "").strip()
            except:
                spiderUtil.log_level(9, response.url)

            try:
                content_time = response.xpath("""//ul[@class="list"]/li[1]/text()""").extract()
                public_time = str(content_time[0]).replace("发布日期：","").strip()
            except:
                spiderUtil.log_level(8, response.url)

            source = "http://www.jl.gov.cn/"

            try:
                content_detail = response.xpath("""//div[@id="zoom"]//text()""").extract()
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


