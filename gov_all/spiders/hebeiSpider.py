#!/usr/bin/env python 
# encoding: utf-8 


"""
 Created by songyao@mail.ustc.edu.cn on 2019/4/26 下午5:21
 
 Function:  河北省 测试通过
 
""" 


import time
import random
import scrapy
import sys
from gov_all.items import GovAllItem
from gov_all.spiders.util import spiderUtil


class heilongjiangNews(scrapy.Spider):
    name = "hebeiSpider"
    start_url = ["http://www.hebei.gov.cn/"]
    header = spiderUtil.header_util()

    def start_requests(self):
        yield scrapy.Request(url="http://www.hebei.gov.cn/hebei/11937442/10761139/index.html", callback=self.parse_item_page_list,headers=self.header)

    def parse_item_page_list(self, response):
        detail_urls = response.xpath("//div[2]/div[2]/div/ul/li/a/@href").extract()
        for detail_url in detail_urls:
            if not detail_url.startswith("http"):
                url = "http://www.hebei.gov.cn" + detail_url
                yield scrapy.Request(url=url, callback=self.parse, headers=self.header)

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)
            try:
                title = response.xpath("""//h2[@class="cont_title"]/text()""").extract()[0]
            except:
                spiderUtil.log_level(6, response.url)
            try:
                author="河北省人民政府网"
            except:
                spiderUtil.log_level(9, response.url)

            try:
                public_timess = response.xpath("""//li[@class="xl_shijian"]//text()""").extract()[0]
                public_times = str(public_timess).replace("年", "-").replace("月", "-").replace("日", "").strip()
                public_time = str(public_times)+" 00:00:00"
            except:
                spiderUtil.log_level(8, response.url)

            try:
                content_arr = response.xpath("//div[@id='zoom']/p/text()").extract()
                content = "".join(content_arr)
            except:
                spiderUtil.log_level(7, response.url)

            source = "http://www.hebei.gov.cn/"

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




