#!/usr/bin/env python 
# encoding: utf-8 


"""
 Created by songyao@mail.ustc.edu.cn on 2019/4/30 下午2:38
 
 Function: 湖北省 http://www.hubei.gov.cn/zwgk/hbyw/hbywqb/ 测试通过
 
""" 


import scrapy
import sys
from gov_all.spiders.util import spiderUtil
from gov_all.items import GovAllItem
import time
import random

class moNews(scrapy.Spider):
    name = "hubeiSpider"
    start_url = "http://www.hubei.gov.cn/zwgk/hbyw/hbywqb/"
    header = spiderUtil.header_util()

    def start_requests(self):
        yield scrapy.Request(url="http://www.hubei.gov.cn/zwgk/hbyw/hbywqb/", callback=self.parse_item_page_list, headers=self.header)

    def parse_item_page_list(self, response):
        detail_urls = response.xpath("//div[@class='container']//li/a/@href").extract()
        for detail_url in detail_urls:
            if "./" in detail_url:
                time.sleep(random.uniform(1, 3))
                deurl = "http://www.hubei.gov.cn/zwgk/hbyw/hbywqb/" + str(detail_url).replace("./","")
                yield scrapy.Request(url=deurl, callback=self.parse, headers=self.header)

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)
            try:
                title = response.xpath("""//*[@class='text-center']/text()""").extract()[0]
            except:
                spiderUtil.log_level(6, response.url)

            try:
                author = str(response.xpath("""//*[@class='list-unstyled list-inline']/li[2]/span/text()""").extract()[0]).replace("来源：","")
            except:
                spiderUtil.log_level(9, response.url)

            try:
                public_time = str(response.xpath("""//*[@class='list-unstyled list-inline']/li[1]/span/text()""").extract()[0]).replace("发布时间：","").strip() + ":00"
            except:
                spiderUtil.log_level(8, response.url)

            source = "http://www.hubei.gov.cn/"

            try:
                content_detail = response.xpath("""//*[@class='TRS_Editor']//text()""").extract()
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
                    yield item
            except:
                pass
        else:
            spiderUtil.log_level(response.status_code, response.url)



