#!/usr/bin/env python
# encoding: utf-8

import datetime
import socket
import re
from elasticsearch import Elasticsearch
from elasticsearch import helpers
import time
import sys
import os
import logging

# elasticsearch集群ip
es_ip = "192.168.1.73"
# es_ip = "10.6.6.64"
# 请求接口的ip
interface_ip = "192.168.1.85"
# interface_ip = "10.6.6.74"
# es_index
es_index = "news_data"
# 日志保存位置及日志文件名
logname = "news_data"
logpath = "./"


# 请求头自动更新
def header_util():
    import random

    user_agents = [
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/57.0.2987.133 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/603.1.30 (KHTML, like Gecko) '
        'Version/10.1 Safari/603.1.30',
        'Mozilla/5.0 (X11; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0',
        'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5; en-US; rv:1.9.1b3) Gecko/20090305 Firefox/3.1b3 GTB5',
        'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89'
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)',
        'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 '
        'Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36'
    ]
    random_headers = {
        'User-Agent': random.choice(user_agents),
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Connection': 'close'
    }
    return random_headers


# 抽取关键词
def get_polarity_keyword(x, url):
    import hashlib
    import requests
    try:
        urlx = "http://" + interface_ip + ":8088/sentiment?text="
        text1 = x
        response = requests.post(urlx, text1.encode('utf-8'))
        text = response.content.decode('utf8')
        alldata = re.split(r',', text)
        find_float = lambda x: re.search("\d+(\.\d+)?", x).group()
        positive = find_float(alldata[2])
        negative = find_float(alldata[1])
        jixing = re.split(r'\"\:\"', alldata[0])
        regex_str = ".*?([\u4E00-\u9FA5]+)"
        match_obj = re.match(regex_str, jixing[1])
        if match_obj:
            polarity = match_obj.group(1)

        url1 = "http://" + interface_ip + ":8080/keyas/outline?text="
        url2 = "http://" + interface_ip + ":8080/keyas/keyword?text="
        text = x
        response1 = requests.post(url1, text.encode('utf-8'))
        response2 = requests.post(url2, text.encode('utf-8'))
        outline = response1.content.decode('utf8')
        keyword = response2.content.decode('utf8')
        keyword_md5_data = keyword
        m = hashlib.md5(keyword_md5_data.encode("utf8"))
        keyword_md5 = str(m.hexdigest())
        dict_polarity = {'negative': negative, 'polarity': polarity, 'positive': positive, 'keywords': keyword,
                         'summary': outline, 'keyword_md5': keyword_md5}
        return dict_polarity
    except:
        log_level(10, url)


# 获取ip地址
def get_local_ip():
    local_ip = ""
    try:
        socket_objs = [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]
        ip_from_ip_port = [(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in socket_objs][0][1]
        ip_from_host_name = [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if
                             not ip.startswith("127.")][:1]
        local_ip = [l for l in (ip_from_ip_port, ip_from_host_name) if l][0]
    except (Exception) as e:
        print("get_local_ip found exception : %s" % e)
    return local_ip if ("" != local_ip and None != local_ip) else socket.gethostbyname(socket.gethostname())


# 存到es
# def save2es_news_data(es_index, title, source, data_id, author, public_time, content, domain, praise_num, url, ip,
#                       crawl_time, source_type, negative, polarity, positive, keywords, summary, keyword_md5, html_size):
#     try:
#         actions = []
#         es = Elasticsearch([{"host": es_ip, "port": 9200, "timeout": 15000}])
#         action = {
#             "_index": es_index,
#             "_type": "data",
#             "_source": {
#                 'title': title,
#                 'source': source,
#                 'data_id': data_id,
#                 'author': author,
#                 'public_time': public_time,
#                 'content': content,
#                 'domain': domain,
#                 'praise_num': praise_num,
#                 'url': url,
#                 'ip': ip,
#                 'crawl_time': crawl_time,
#                 'negative': negative,
#                 'polarity': polarity,
#                 'positive': positive,
#                 'keywords': keywords,
#                 'summary': summary,
#                 'source_type': source_type,
#                 'keyword_md5': keyword_md5
#             }
#         }
#
#         actions.append(action)
#         if len(action) == 1000:
#             helpers.bulk(es, actions)
#             del actions[0:len(action)]
#
#         helpers.bulk(es, actions)
#         text2es = str(title) + str(source) + str(data_id) + str(author) + str(public_time) + str(domain) + str(
#             url) + str(ip) + str(crawl_time) + str(negative) + str(polarity) + str(positive) + str(keywords) + str(
#             summary) + str(source_type) + str(keyword_md5)
#         es_size = sys.getsizeof(text2es)
#         logger_info = "|" + es_index + "|" + crawl_time + "|" + str(html_size) + "|" + ip + "|" + str(
#             es_size) + "|" + url + "|1|200_SUCCESS" + "|&|" + title + "|&|" + source + "|&|" + data_id + "|&|" + author + "|&|" + public_time + "|&|" + content + "|&|" + domain + "|&|" + praise_num + "|&|" + negative + "|&|" + polarity + "|&|" + positive + "|&|" + keywords + "|&|" + keyword_md5 + "|&|" + summary + "|&|" + source_type
#         logger_util.info(logger_info)
#     except Exception as e:
#         log_level(11, url)


# 获取当前时间
def get_time():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))


# 获取当前时间的前一个小时时间
def get_first_hour():
    tim = datetime.datetime.now()
    # datetime.timedelta(days=0, seconds=0, microseconds=0)#毫秒, milliseconds=0, minutes=0, hours=0, weeks=0)
    first_hour = (tim + datetime.timedelta(hours=-1)).strftime("%Y-%m-%d %H")
    return first_hour


# 获取当前时间的前两个小时时间
def get_first_threehour():
    tim = datetime.datetime.now()
    # datetime.timedelta(days=0, seconds=0, microseconds=0)#毫秒, milliseconds=0, minutes=0, hours=0, weeks=0)
    first_hour = (tim + datetime.timedelta(hours=-2)).strftime("%Y-%m-%d %H")
    return first_hour


# 获取当前时间的前三个小时时间
def get_first_twohour():
    tim = datetime.datetime.now()
    # datetime.timedelta(days=0, seconds=0, microseconds=0)#毫秒, milliseconds=0, minutes=0, hours=0, weeks=0)
    first_hour = (tim + datetime.timedelta(hours=-3)).strftime("%Y-%m-%d %H")
    return first_hour


# 获取当前时间的前一天的时间
def get_yesterday_date():
    tim = datetime.datetime.now()
    yesterday_date = (tim + datetime.timedelta(days=-1)).strftime("%Y-%m-%d")
    return yesterday_date


"""
status（状态码）	log_message（提示信息）	备注
1		        SUCCESS		            请求、解析和存储成功
2		        403_Forbidden		    403请求访问被禁止
3		        404_NotFound		    404服务器无法回应
4		        301_Redirect		    301请求重定向错误
5		        Other_RequestError		其他请求错误
6		        Title_AnalysisError		标题解析错误
7		        Content_AnalysisError	正文解析错误
8		        Time_AnalysisError		时间解析错误
9		        Author__AnalysisError	作者解析错误
10		        Other_AnalysisError		其他解析错误
11		        Save_Error		        存es错误
"""


# 日志系统
class logger_util:
    logsize = 1024 * 1024 * int(80000)
    lognum = int(3)
    logname = os.path.join(logpath, logname)
    logname = logname + ".log"

    log = logging.getLogger()
    formatter = logging.Formatter('[%(asctime)s][log.py][line:%(lineno)d][%(levelname)s] %(message)s',
                                  '%Y-%m-%d %H:%M:%S')

    handle = logging.FileHandler(logname)
    handle.setFormatter(formatter)

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    # 给logger添加handler
    log.addHandler(handle)
    log.addHandler(console)
    log.setLevel(logging.INFO)

    @classmethod
    def info(cls, msg):
        cls.log.info(msg)
        return

    @classmethod
    def warning(cls, msg):
        cls.log.warning(msg)
        return

    @classmethod
    def error(cls, msg):
        cls.log.error(msg)
        return


# 获取日志错误信息
def log_message(code):
    httpcode_dict = {200: "200_SUCCESS",
                     301: "301_Redirect",
                     404: "404_NotFound",
                     403: "403_Forbidden",
                     6: "Title_AnalysisError",
                     7: "Content_AnalysisError",
                     8: "Time_AnalysisError",
                     9: "Author_AnalysisError",
                     10: "Other_AnalysisError",
                     11: "Save_Error"}
    message = httpcode_dict.get(code)
    if message:
        return message
    else:
        return "Other_RequestError"


# 获取日志错误状态码
def log_status(code):
    httpcode_dict = {200: "1",
                     403: "2",
                     404: "3",
                     301: "4",
                     6: "6",
                     7: "7",
                     8: "8",
                     9: "9",
                     10: "10",
                     11: "11"}
    message = httpcode_dict.get(code)
    if message:
        return message
    else:
        return "5"


# 日志信息
def log_level(code, url):
    error = "|" + es_index + "|" + get_time() + "|" + "0" + "|" + get_local_ip() + "|" + "0" + "|" + str(
        url) + "|" + log_status(code) + "|" + log_message(code)
    logger_util.error(error)
