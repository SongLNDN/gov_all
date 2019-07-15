# coding= utf-8

import scrapy


class GovAllItem(scrapy.Item):
    source = scrapy.Field()
    content = scrapy.Field()
    public_time = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    crawl_time = scrapy.Field()
    html_size = scrapy.Field()