import math

from dao.mongo_db import MongoDB
from models.keywords.tfidf import Segment
from datetime import datetime
import re


class ContentLabel(object):
    def __init__(self):
        self.seg = Segment(stopword_files=['../../data/stopwords/1.txt', '../../data/stopwords/2.txt',
                                           '../../data/stopwords/3.txt',
                                           '../../data/stopwords/4.txt'], userdict_files=[])
        self.mongo_scrapy = MongoDB(db='scrapy_data')
        self.mongo_recommendation = MongoDB(db='recommendation')
        self.scrapy_collection = self.mongo_scrapy.db_scrapy['content_ori']
        self.content_label_collection = self.mongo_recommendation.db_recommendation['content_label']

    def get_data_from_mongodb(self):
        datas = self.scrapy_collection.find()
        return datas

    def get_keywords(self, contents, num=10):
        keyword = self.seg.combined_keyword(contents, num)
        return keyword

    def get_words_nums(self, contents):
        ch = re.findall('([\u4e00-\u9fa5])', contents)
        num = len(ch)
        return num

    def update_content_hot(self):
        datas = self.content_label_collection.find()
        for data in datas:
            self.content_label_collection.update_one({"_id": data['_id']}, {
                "$set": {"hot_heat": self.hot_time_alpha(data['hot_heat'], data['news_date'])}})

    def hot_time_alpha(self, hot_value, news_date, alpha=0.01):
        # Calculate the difference in days between the current time and the news time
        day = (datetime.now() - news_date).days
        hot = hot_value / math.pow(day + 1, alpha)
        return hot

    def make_content_labels(self):
        datas = self.get_data_from_mongodb()
        for data in datas:
            content_collection = dict()
            content_collection['describe'] = data['desc']
            content_collection['type'] = data['type']
            content_collection['title'] = data['title']
            content_collection['news_date'] = data['times']
            content_collection['hot_heat'] = 10000
            content_collection['likes'] = 0
            content_collection['read'] = 0
            content_collection['collections'] = 0
            content_collection['create_time'] = datetime.utcnow()
            content_collection['words_num'] = self.get_words_nums(data['desc'])
            content_collection['keywords'] = self.get_keywords(data['desc'], 10)
            self.content_label_collection.insert_one(content_collection)


if __name__ == '__main__':
    content = ContentLabel()
    content.make_content_labels()
    content.update_content_hot()
