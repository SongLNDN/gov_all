#!/usr/bin/env python 
# encoding: utf-8 


"""
 Created by songyao@mail.ustc.edu.cn on 2019/4/30 上午10:56
 
 Function:  江西省爬虫
 
""" 

import scrapy
import sys

from lxml import etree

from gov_all.spiders.util import spiderUtil
from gov_all.items import GovAllItem

class moNews(scrapy.Spider):
    name = "jiangxiSpider"
    start_url = "http://www.jiangxi.gov.cn/"
    header = spiderUtil.header_util()

    def start_requests(self):
        yield scrapy.Request(url="http://www.jiangxi.gov.cn/col/col393/index.html", callback=self.parse_item_page_list, headers=self.header)
        # 全量爬取历史数据
        # for i in range(2,917):
        #     url = "http://www.jiangxi.gov.cn/col/col393/index.html?uid=45663&pageNum="+str(i)
        #     yield scrapy.Request(url=url, callback=self.parse_item_page_list, headers=self.header)


    def parse_item_page_list(self, response):
        s = response.xpath("//script[@type='text/xml']/text()").extract()[0]
        detail_urls = etree.HTML(s).xpath("//a/@href")
        for detail_url in detail_urls:
            detail_url = "http://www.jiangxi.gov.cn" + detail_url
            yield scrapy.Request(url=detail_url, callback=self.parse, headers=self.header)

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)
            try:
                content_title = response.xpath("""//div[@class='artile_zw']/div/p/text()""").extract()
                title = "".join(content_title).strip()
                print(title)
            except:
                spiderUtil.log_level(6, response.url)

            try:
                author = response.xpath("""//div[@id='zoom']//font/text()[2]""").extract()[0]

            except:
                spiderUtil.log_level(9, response.url)

            try:
                content_time = response.xpath("""//div[@class='sp_time screen']/font[1]/text()""").extract()[0]
                public_time = str(content_time).replace("发布时间：","")
            except:
                spiderUtil.log_level(8, response.url)

            source = "http://www.jiangxi.gov.cn/"

            try:
                content_detail = response.xpath("""//div[@id='zoom']/p/text()""").extract()
                content = "".join(content_detail)
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


