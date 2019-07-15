#!/usr/bin/env python 
# coding: utf-8 
"""
@author: TongYao
@file:   scSpider.py
@time:  2019-04-30 
@function: 四川省政府网站新闻爬虫
"""
import re
import sys
import scrapy
from gov_all.items import GovAllItem
from gov_all.spiders.util import spiderUtil


class scNews(scrapy.Spider):
    name = "scSpider"
    start_url = ["http://www.sc.gov.cn/10462/10705/10709/xwfbt_list.shtml",
                 "http://www.sc.gov.cn/10462/10705/10708/xwfbt_list.shtml",
                 "http://www.sc.gov.cn/10462/10705/10707/xwfbt_list.shtml",
                 "http://www.sc.gov.cn/10462/10705/10706/xwfbt_one.shtml"]

    header = spiderUtil.header_util()

    def start_requests(self):
        for url in self.start_url:
            # time.sleep(random.uniform(3, 5))
            yield scrapy.Request(url=url, callback=self.parse_item_page_list, headers=self.header)
            # if "list" in url:
            #     for page in range(1, 6):
            #         list_url = url.split(".shtml")[0]+"_"+str(page)+".shtml"
            #         yield scrapy.Request(url=list_url, callback=self.parse_item_page_list, headers=self.header)

    def parse_item_page_list(self, response):
        news_list = response.xpath("//td/a/@href").extract()
        for url in news_list:
            if not url.startswith("http"):
                news_url = "http://www.sc.gov.cn"+url
                yield scrapy.Request(url=news_url, callback=self.parse, headers=self.header)

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)

            try:
                title_arr = response.xpath("//h2/ucaptitle/text()").extract()
                title = "".join(title_arr).strip()
            except:
                spiderUtil.log_level(6, response.url)

            try:
                author_arr = response.xpath("//ul[@id='articleattribute']/li/text()").extract()
                author = "".join(author_arr).strip()
                if author == "":
                    author = "四川省人民政府"
            except:
                spiderUtil.log_level(9, response.url)

            try:
                public_time = re.search(r"(\d{4}年\d{1,2}月\d{1,2}日\s\d{1,2}时\d{1,2}分)", response.text).group(0).replace("年","-").replace("月","-").replace("日","").replace("时",":").replace("分","")+":00"
            except:
                # spiderUtil.log_level(8, response.url)
                pass
            try:
                content_arr = response.xpath("//div[@id='cmsArticleContent']")[0].xpath('string(.)').extract()
                content = "".join(content_arr)
            except:
                spiderUtil.log_level(7, response.url)

            source = "http://www.sc.gov.cn/"

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