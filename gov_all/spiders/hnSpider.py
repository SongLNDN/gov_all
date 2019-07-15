#!/usr/bin/env python 
# coding: utf-8 
"""
@author: TongYao
@file:   hnSpider.py
@time:  2019-04-30 
@function: 海南省政府网站新闻爬虫
"""
import re
import scrapy
import sys
from gov_all.items import GovAllItem
from gov_all.spiders.util import spiderUtil


class hnNews(scrapy.Spider):
    name = "hnSpider"
    start_url = ["http://www.hainan.gov.cn/hainan/tingju/list3.shtml",
                 "http://www.hainan.gov.cn/hainan/sxian/list3.shtml",
                 "http://www.hainan.gov.cn/hainan/5309/list3.shtml",
                 "http://www.hainan.gov.cn/hainan/mtkhn/list3.shtml",
                 "http://www.hainan.gov.cn/hainan/ldhd/sj_list3.shtml"]

    header = spiderUtil.header_util()

    def start_requests(self):
        for url in self.start_url:
            # time.sleep(random.uniform(3, 5))
            yield scrapy.Request(url=url, callback=self.parse_item_page_home, headers=self.header)

    def parse_item_page_home(self, response):
        yield scrapy.Request(url=response.url, callback=self.parse_item_page_list, headers=self.header,dont_filter=True)

    def parse_item_page_list(self, response):
        news_list = response.xpath("//div[@class='list-right_title fon_1']/a/@href").extract()
        for news_url in news_list:
            if not news_url.startswith("http"):
                news_url = "http://www.hainan.gov.cn"+news_url
                yield scrapy.Request(url=news_url, callback=self.parse, headers=self.header)

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)

            try:
                title = response.xpath("//div[@class='title_cen mar-t2 text']/ucaptitle/text()").extract()[0].strip()
            except:
                spiderUtil.log_level(6, response.url)

            try:
                author = response.xpath("//span[@id='ly']/text()").extract()
                if author == []:
                    author = "海南省人民政府"
                else:
                    author = author[0]
            except:
                spiderUtil.log_level(9, response.url)

            try:
                public_time = re.search(r"(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2})", response.text).group(0)+":00"
            except:
                spiderUtil.log_level(8, response.url)

            try:
                content_arr = response.xpath("//div[@id='zoom']/div[@id='font']/ucapcontent/p/text()").extract()
                content = "".join(content_arr)
            except:
                spiderUtil.log_level(7, response.url)

            source = "http://www.hainan.gov.cn/"

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
