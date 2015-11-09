# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
from scrapy.utils.serialize import ScrapyJSONEncoder
_encoder = ScrapyJSONEncoder()

class GizmodoPipeline(object):
    def process_item(self, item, spider):
        return item


class JsonWriterPipeline(object):

    def __init__(self):
        self.file = open('gizmodo_items.json', 'wb')

    def process_item(self, item, spider):
        self.file.write(_encoder.encode(item))
        self.file.write('\n')
        return item


# with open('gizmodo_items.json') as f:
#     for line in f:
#         data.append(json.loads(line))