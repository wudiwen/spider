# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
class ImageproPipeline(object):
    

    def open_spider(self, spider):
        self.fp = open('pic.txt', 'w', encoding='utf8')

    # 这个方法会自动调用，每次来一个item都会调用这个方法
    def process_item(self, item, spider):
        d = dict(item)
        string = json.dumps(d, ensure_ascii=False)
        self.fp.write(string + '\n')
        return item


    def close_spider(self, spider):
        self.fp.close()
