#!/usr/bin/env python 
# encoding: utf-8 


"""
 Created by songyao@mail.ustc.edu.cn on 2019/4/30 上午9:43
 
 Function: 安徽省爬虫 测试通过
 
""" 

import scrapy
import sys
from gov_all.spiders.util import spiderUtil
from gov_all.items import GovAllItem

class moNews(scrapy.Spider):
    name = "anhuiSpider"
    start_url = "http://www.ah.gov.cn/"
    header = spiderUtil.header_util()

    def start_requests(self):
        yield scrapy.Request(url="http://www.ah.gov.cn/UserData/SortHtml/1/549213957.html", callback=self.parse_item_page_list, headers=self.header)
        # for i in range(2,524):
        #     url = "http://www.ah.gov.cn/tmp/Nav_nav.shtml?SS_ID=7&tm=29357.31&Page="+str(i)
        #     yield scrapy.Request(url=url, callback=self.parse_item_page_list, headers=self.header)

    def parse_item_page_list(self, response):
        url_list = response.xpath("//div[@class='navjz']//a/@href").extract()
        for url in url_list:
            if "http://www.ah.gov.cn" in url:
                yield scrapy.Request(url=url, callback=self.parse, headers=self.header, dont_filter=True)

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)
            try:
                titles = response.xpath("""//div[@class='wztit']//text()""").extract()
                title = "".join(titles).strip()
            except:
                spiderUtil.log_level(6, response.url)

            try:
                author_arr = response.xpath("""//div[@class='wzbjxx']/p/text()[3]""").extract()
                author = "".join(author_arr).replace("来源：", "").strip()
            except:
                spiderUtil.log_level(9, response.url)

            try:
                content_date = response.xpath("""//div[@class='wzbjxx']/p/text()[1]""").extract()[0]
                content_time = response.xpath("""//div[@class='wzbjxx']/p/text()[2]""").extract()[0]
                public_time = str(content_date)+" "+str(content_time)+":00"
            except:
                spiderUtil.log_level(8, response.url)

            source = "http://www.ah.gov.cn/"

            try:
                content_detail = response.xpath("""//div[@class='wzcon']//text()""").extract()
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
            spiderUtil.log_level(response.status_code, response.url)



