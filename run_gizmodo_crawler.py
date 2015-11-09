"""
Crawl all articles

"""

import scrapy
from scrapy.crawler import CrawlerProcess
from gizmodo.spiders.gizmodo_web_crawl_spider import GizmodoSpider
from scrapy.utils.project import get_project_settings


process = CrawlerProcess(get_project_settings())

process.crawl(GizmodoSpider)
process.start()