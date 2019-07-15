#!/usr/bin/env python 
# encoding: utf-8 


"""
 Created by songyao@mail.ustc.edu.cn on 2019/4/30 上午9:55
 
 Function: 福建省人民政府 http://www.fujian.gov.cn/ 测试通过
 
""" 


import scrapy
import sys
from gov_all.spiders.util import spiderUtil
from gov_all.items import GovAllItem

class moNews(scrapy.Spider):
    name = "fujianSpider"
    start_url = "http://www.fujian.gov.cn/"
    header = spiderUtil.header_util()

    def start_requests(self):
        yield scrapy.Request(url="http://www.fujian.gov.cn/xw/fjyw/", callback=self.parse_item_page_list, headers=self.header)

    def parse_item_page_list(self, response):
        url_list = response.xpath("//ul[@class='list-gl']//a/@href").extract()
        for urls in url_list:
            url =  "http://www.fujian.gov.cn/xw/fjyw/" + str(urls).replace("./","")
            yield scrapy.Request(url=url, callback=self.parse, headers=self.header)

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)
            try:
                title_arr = response.xpath("""//div[@class='xl-nr clearflx']//h3/text()""").extract()
                title = "".join(title_arr).strip()
            except:
                spiderUtil.log_level(6, response.url)

            try:
                author_arr = response.xpath("""//div[@class='xl-nr clearflx']//h5/span/text()""").extract()
                author = "".join(author_arr).replace("[", "").replace("]", "").strip()
            except:
                spiderUtil.log_level(9, response.url)

            try:
                content_time = response.xpath("""//div[@class='xl-nr clearflx']//h5/text()""").extract()
                public_time = "".join(content_time).replace("字号：","").replace("|","").strip()
                public_time = str(public_time)+":00"
            except:
                spiderUtil.log_level(8, response.url)

            source = "http://www.fujian.gov.cn/"

            try:
                content_detail = response.xpath("""//div[@class='TRS_Editor']//text()""").extract()
                content = "".join(content_detail).strip()
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
            spiderUtil.log_level(response.status, response.url)




