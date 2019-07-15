# coding= utf-8
from gov_all.spiders.util import spiderUtil


class GovAllPipeline(object):
    def process_item(self, item, spider):
        source = item["source"]
        content = item["content"]
        public_time = item["public_time"]
        url = item["url"]
        title = item["title"]
        author = item["author"]
        crawl_time = item["crawl_time"]
        html_size = item["html_size"]

        dict = spiderUtil.get_polarity_keyword(content, url)
        negative = dict.get("negative")
        positive = dict.get("positive")
        polarity = dict.get("polarity")
        keywords = dict.get("keywords")
        summary = dict.get("summary")
        keyword_md5 = dict.get("keyword_md5")

        es_index = "gmw_news_data"
        data_id = ""
        source_type = "新闻"
        domain = "政府"
        praise_num = ""

        if keyword_md5 != "d41d8cd98f00b204e9800998ecf8427e":
            ip = spiderUtil.get_local_ip()

            spiderUtil.save2es_news_data(es_index, title, source, data_id, author, public_time, content,
                                         domain,
                                         praise_num, url, ip,
                                         crawl_time,
                                         source_type, negative, polarity, positive, keywords, summary,
                                         keyword_md5, html_size)
