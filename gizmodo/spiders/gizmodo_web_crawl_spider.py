"""
Use this script to crawl all of Gizmodo's articles

"""
import scrapy
import requests
import math

from gizmodo.items import GizmodoItem, GizmodoComment
from scrapy.contrib.spiders import Rule
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.exceptions import CloseSpider

global NUM_ARTICLES
NUM_ARTICLES = 2000

class GizmodoSpider(scrapy.Spider):

    name = "gizmodo"
    # allowed_domains = ["gizmodo.com", "io9.com", "foxtrotalpha.jalopnik.com"]
    allowed_domains = ["gizmodo.com"]
    start_urls = [
        "http://gizmodo.com",
    ]

    # def process_value(x):
    #     print 'LOOK AT THIS: ', 'http://gizmodo.com/' + x
    #     return 'http://gizmodo.com/' + x

    # extractor = LxmlLinkExtractor(allow=(), 
    #                             restrict_css=('.load-more div.text-center a::attr(href)',),
    #                             process_value=(process_value))

    # rules = (
    #     Rule(
    #         extractor, 
    #         callback="parse_headlines", follow= True
    #         ),
    # )

    def parse(self, response):
        # we can't recursively call back this function, 
        #   so we call parse_headlines() instead
        links = response.css('.headline').xpath('./a/@href').extract()
        for url in links:
            yield scrapy.Request(url, callback=self.parse_article)
        link = response.css('.load-more div.text-center a::attr(href)').extract()[0]
        link = 'http://gizmodo.com/' + link
        yield scrapy.Request(link, callback=self.parse_headlines)

    def parse_headlines(self, response):
        # get all headlines per homepage
        links = response.css('.headline').xpath('./a/@href').extract()
        for url in links:
            yield scrapy.Request(url, callback=self.parse_article)
        link = response.css('.load-more div.text-center a::attr(href)').extract()[0]
        link = 'http://gizmodo.com/' + link
        yield scrapy.Request(link, callback=self.parse_headlines)

    def parse_article(self, response):
        global NUM_ARTICLES
        if self.crawler.stats.get_value('item_scraped_count') >= NUM_ARTICLES:
            raise CloseSpider('Done Crawling')

        item = GizmodoItem()
        item['url'] = response.url
        item['title'] = response.xpath("//title/text()").extract()[0].encode('ascii', 'replace')
        item['twitter_url'] = response.xpath('//meta[contains(@name, "twitter:url")]/@content').extract()[0]
        
        keywords_ex = response.xpath('//meta[contains(@name, "keywords")]/@content').extract()
        keywords = []
        for k in keywords_ex:
            k = k.split(',')
            keywords.extend(k)
        keywords = list(set(keywords))
        item['keywords'] = keywords
        
        item['description'] = response.xpath('//meta[contains(@name, "description")]/@content').extract_first()
        item['author'] = response.css('.display-name').xpath('./a/text()').extract()
        item['author_link'] = response.css('.display-name').xpath('./a/@href').extract()[0]
        item['created_millis'] = response.css('.publish-time').xpath('./@data-publishtime').extract()        

        # Extract body elements that are only text
        # body_class = response.css('.post-content').xpath('./p/@class')
        body = response.css('.post-content').xpath('./p')
        img_idx = []
        vid_idx = []
        text_idx = []
        for idx, b in enumerate(body):
            if b.re('has-image'):
                img_idx.append(idx)
            elif b.re('has-video'):
                vid_idx.append(idx)
            else:
                text_idx.append(idx)
        body_img = [body[i].xpath('.//img/@src').extract() for i in img_idx]
        # body_vid = [body[i] for i in vid_idx]
        body_text = [' '.join(body[i].xpath('.//text()').extract()) for i in text_idx]
        item['body_imgs'] = body_img
        item['body_text'] = body_text

        num_like = response.css('.js_like_count').xpath('./text()').extract()[0]
        num_reply = response.css('.js_reply-count').xpath('./text()').extract()[0]
        item['num_reply'] = num_reply
        item['num_like'] = num_like

        # Comments
        comments = list()
        blog_id = response.css('.top-tools').xpath('./ul/li/@data-blogid').extract()[0]
        post_id = response.css('.post-dropdown-ct').xpath('./ul/@data-postid').extract()[0]
        # We can only get 100 comments at a time
        # But we can only specify the number of replies we want,
        #   meaning we will get many more children per reply for each call
        #   So we resort to getting just 5 replies per call
        num_increment = 5
        for i in xrange(0, int(num_reply), num_increment):
            comments_url = 'http://gizmodo.com/api/core/reply/' + \
                                '%s/replies?currentBlogId=' % (post_id) + \
                                '%s&startIndex=%s&maxReturned=' % (blog_id, i) + \
                                '%s&withLikeCounts=true' % (num_increment) + \
                                '&maxChildren=%s&approvedChildrenOnly=true' % (num_reply) + \
                                '&approvedStartersOnly=true&cache=true' 
            # if parse_comments return nothing, then break
            # append to comments otherwise
            comm = self.parse_comments(comments_url)
            if not comm:
                break
            else:
                comments.extend(comm)

        item['comments'] = comments

        yield item

    def parse_comments(self, comments_url):
        """
            takes:      url to get comments from
            returns:    list of {'reply': r, 'children': c}
        """
        r = requests.get(comments_url)
        comments = r.json()
        
        if not comments:
            return None

        replyCount = comments['data']['directReplyCount']
        comments = comments['data']['items']
        commentsListObj = []
        for c in comments:
            commentsListObj.append(self.get_all_comment_objects(c))

        return commentsListObj

    def get_all_comment_objects(self, comment):
        """
            takes: list
            return: dict of GizmodoComments
        """
        reply = comment['reply']
        reply = self.get_comment_object(reply)
        children = comment['children']['items']
        childrenObj = []
        for c in children:
            childrenObj.append(self.get_comment_object(c))

        return {'reply': reply, 'children': childrenObj}

    def get_comment_object(self, comment):
        """  
            takes: dict
            return: GizmodoComment
        """
        gizmodo_comment = GizmodoComment()   
        try:
            # this needs to be fixed
            gizmodo_comment['parent_uid'] = comment['parentAuthorId']
            gizmodo_comment['parent_name'] = comment['replyMeta']['parentAuthor']['displayName']
        except:
            gizmodo_comment['parent_uid'] = None
            gizmodo_comment['parent_name'] = None
        gizmodo_comment['length'] = comment['length']
        gizmodo_comment['likes'] = comment['likes']
        gizmodo_comment['author_uid'] = comment['author']['id']
        gizmodo_comment['author_name'] = comment['author']['displayName']
        gizmodo_comment['text'] = comment['plaintext']
        gizmodo_comment['time'] = comment['publishTimeMillis']
        gizmodo_comment['timezone'] = comment['timezone']
        gizmodo_comment['images'] = [c['uri'] for c in comment['images']]
        gizmodo_comment['videos'] = [v['src'] for v in comment['videos']]        
        return gizmodo_comment
