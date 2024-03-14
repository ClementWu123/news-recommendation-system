# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from .dao.mongo_db import MongoDB


class SinaPipeline:
    def __init__(self):
        self.mongo = MongoDB(db='scrapy_data')
        self.collection = self.mongo.db_scrapy['content']

    def process_item(self, item, spider):
        result_item = dict(item)
        self.collection.insert_one(result_item)
        return item
