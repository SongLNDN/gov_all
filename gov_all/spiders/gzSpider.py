#!/usr/bin/env python 
# coding: utf-8 
"""
@author: TongYao
@file:   gzSpider.py
@time:  2019-04-30 
@function: 贵州政府网站新闻爬虫
"""
import re
import scrapy
import sys
from gov_all.items import GovAllItem
from gov_all.spiders.util import spiderUtil


class gzNews(scrapy.Spider):
    name = "gzSpider"
    start_url = ["http://www.guizhou.gov.cn/xwdt/rmyd/",
                 "http://www.guizhou.gov.cn/xwdt/jrgz/",
                 "http://www.guizhou.gov.cn/xwdt/gzyw/",
                 "http://www.guizhou.gov.cn/xwdt/qgyw/",
                 "http://www.guizhou.gov.cn/xwdt/mtkgz/",
                 "http://www.guizhou.gov.cn/xwdt/djfb/",
                 "http://www.guizhou.gov.cn/xwdt/tzgg/",
                 "http://www.guizhou.gov.cn/xwdt/szf/ldjh/",
                 "http://www.guizhou.gov.cn/xwdt/szf/ldhd/",
                 "http://www.guizhou.gov.cn/xwdt/dt_22/bm/",
                 "http://www.guizhou.gov.cn/xwdt/dt_22/df/gy/index.html",
                 "http://www.guizhou.gov.cn/xwdt/dt_22/df/zy/",
                 "http://www.guizhou.gov.cn/xwdt/dt_22/df/lps/",
                 "http://www.guizhou.gov.cn/xwdt/dt_22/df/as/",
                 "http://www.guizhou.gov.cn/xwdt/dt_22/df/bj/",
                 "http://www.guizhou.gov.cn/xwdt/dt_22/df/tr/",
                 "http://www.guizhou.gov.cn/xwdt/dt_22/df/qdn/",
                 "http://www.guizhou.gov.cn/xwdt/dt_22/df/qn/",
                 "http://www.guizhou.gov.cn/xwdt/dt_22/df/qxn/",
                 "http://www.guizhou.gov.cn/xwdt/dt_22/df/gaxq/"]

    header = spiderUtil.header_util()

    def start_requests(self):
        for url in self.start_url:
            # time.sleep(random.uniform(3, 5))
            yield scrapy.Request(url=url, callback=self.parse_item_page_home, headers=self.header)

    def parse_item_page_home(self, response):
        yield scrapy.Request(url=response.url, callback=self.parse_item_page_list, headers=self.header,dont_filter=True)
        # max_page = response.xpath("//div[@class='page']/script/text()").extract()[0].split("HTML(")[1].split(",")[0]
        # for page in range(1, int(max_page)):
        #     news_list_url = response.url + "index_" + str(page) + ".html"
        #     # time.sleep(random.uniform(3, 5))
        #     yield scrapy.Request(url=news_list_url, callback=self.parse_item_page_list, headers=self.header)

    def parse_item_page_list(self, response):
        news_list = response.xpath("//div[@class='right-list-box']/ul/li/a/@href").extract()
        for news_url in news_list:
            # time.sleep(random.uniform(3, 5))
            yield scrapy.Request(url=news_url, callback=self.parse, headers=self.header)

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)

            try:
                title = response.xpath("//h1/text()").extract()[0]
            except:
                spiderUtil.log_level(6, response.url)

            try:
                author = response.xpath("//head/meta[@name='ContentSource']/@content").extract()
                if author == []:
                    author = "贵州省人民政府"
                else:
                    author = author[0]
            except:
                spiderUtil.log_level(9, response.url)

            try:
                public_time = re.search(r"(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2})", response.text).group(0)
            except:
                spiderUtil.log_level(8, response.url)

            try:
                content_arr = response.xpath("//div[@class='view TRS_UEDITOR trs_paper_default trs_web']/p/text()").extract()
                content = "".join(content_arr)
            except:
                spiderUtil.log_level(7, response.url)

            source = "http://www.guizhou.gov.cn/"

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
