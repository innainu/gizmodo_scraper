# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class GizmodoItem(scrapy.Item):
    """
        GizmodoItem object, for storing an article's data
    """
    url = scrapy.Field()
    title = scrapy.Field()
    twitter_url = scrapy.Field()
    keywords = scrapy.Field()
    description = scrapy.Field()
    author = scrapy.Field()
    author_link = scrapy.Field()
    created_millis = scrapy.Field()
    body_imgs = scrapy.Field()
    body_text = scrapy.Field()
    num_reply = scrapy.Field()
    num_like = scrapy.Field()
    comments = scrapy.Field()

class GizmodoComment(scrapy.Item):
    """
        GizmodoComment object, for storing a dict of comments
    """
    parent_uid = scrapy.Field()        # original u'authorBlogName
    parent_name = scrapy.Field()       # original u'authorId
    length = scrapy.Field()             # u'length
    likes = scrapy.Field()              # u'likes
    author_uid = scrapy.Field()
    author_name = scrapy.Field()
    text = scrapy.Field()       # u'plaintext
    time = scrapy.Field()       # u'publishTimeMillis
    timezone = scrapy.Field()   #place of comment
    images = scrapy.Field()
    videos = scrapy.Field()

    