#!/usr/bin/env python 
# encoding: utf-8 


"""
 Created by songyao@mail.ustc.edu.cn on 2019/4/30 上午11:14  测试通过
 
 Function:  山东省  测试通过
 
"""
import re

import scrapy
import sys

from lxml import etree

from gov_all.spiders.util import spiderUtil
from gov_all.items import GovAllItem

class moNews(scrapy.Spider):
    name = "shandongSpider"
    start_url = "http://www.shandong.gov.cn/"
    header = spiderUtil.header_util()

    def start_requests(self):
        yield scrapy.Request(url="http://www.shandong.gov.cn/col/col3199/index.html", callback=self.parse_item_page_list, headers=self.header)
        # 全量爬取历史数据
        # for i in range(1,460):
        #     url = "http://www.shandong.gov.cn/col/col3199/index.html?uid=5836&pageNum="+str(i)
        #     yield scrapy.Request(url=url, callback=self.parse_item_page_list, headers=self.header)

    def parse_item_page_list(self, response):
        s = response.xpath("//script[@type='text/xml']/text()").extract()[0]
        detail_urls = etree.HTML(s).xpath("//a/@href")
        for key in detail_urls:
            yield scrapy.Request(url=key, callback=self.parse, headers=self.header, dont_filter=True)

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)
            try:
                title = response.xpath("""//div[@class='xq-tit']/span/text()""").extract()[0]
            except:
                spiderUtil.log_level(6, response.url)

            try:
                author = str(response.xpath("""//div[@class='R-tit']/span[2]/text()""").extract()[0]).replace("来源：","")

            except:
                spiderUtil.log_level(9, response.url)

            try:
                public_time = re.search(r"(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2})", response.text).group(0)
            except:
                spiderUtil.log_level(8, response.url)

            source = "http://www.shangdong.gov.cn/"

            try:
                content_detail = response.xpath("""//div[@class='article']//text()""").extract()
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
                    # print(item)
                    yield item

            except:
                pass
        else:
            spiderUtil.log_level(response.status_code, response.url)



