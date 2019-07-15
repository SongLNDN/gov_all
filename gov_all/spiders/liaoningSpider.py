#!/usr/bin/env python 
# encoding: utf-8 


"""
 Created by songyao@mail.ustc.edu.cn on 2019/4/29 下午1:30
 
 Function:  辽宁省
 
""" 


import scrapy
import sys
from gov_all.spiders.util import spiderUtil
from gov_all.items import GovAllItem
import time
import random

class moNews(scrapy.Spider):
    name = "liaoningSpider"
    start_url = "http://www.ln.gov.cn/"
    header = spiderUtil.header_util()

    def start_requests(self):
        yield scrapy.Request(url="http://www.ln.gov.cn/zfxx/jrln/wzxx2018/index.html", callback=self.parse_item_page_list, headers=self.header)
        # for i in range(1,24):
        #     url = "http://www.ln.gov.cn/zfxx/jrln/wzxx2018/index_"+str(i)
        #     yield scrapy.Request(url=url, callback=self.parse_item_page_list, headers=self.header)

    def parse_item_page_list(self, response):
        detail_urls = response.xpath("//ul[@class='list_rul']/li/a/@href").extract()
        for detail_url in detail_urls:
            detail_url = "http://www.ln.gov.cn/zfxx/jrln/wzxx2018/" + detail_url.replace("./", "")
            time.sleep(random.uniform(1, 3))
            yield scrapy.Request(url=detail_url, callback=self.parse, headers=self.header)

    def parse(self, response):
        if response.status == 200:
            text = response.text
            # print(text)
            html_size = sys.getsizeof(text)
            try:
                titles = response.xpath("""//td[@align="center"]/text()""").extract()
                title = "".join(titles).replace("来源：","").strip()
            except:
                spiderUtil.log_level(6, response.url)

            try:
                content_author = response.xpath("""//table[@class="time"]//td[@align="left"]/text()""").extract()
                authors = content_author[0].split("  信息来源：")
                author = str(authors[1])
            except:
                spiderUtil.log_level(9, response.url)

            try:
                content_time = response.xpath("""//table[@class="time"]//td[@align="left"]/text()""").extract()
                public_times = str(content_time[0]).split("  信息来源：")
                public_time = str(str(public_times[0]).replace("发布时间：", "").replace("年", "-").replace("月", "-").replace("日","") + " 00:00:00").strip()

            except:
                spiderUtil.log_level(8, response.url)

            source = "http://www.ln.gov.cn/"

            try:
                content_detail = response.xpath("""//div[@class='TRS_Editor']/div/p/text()""").extract()
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



