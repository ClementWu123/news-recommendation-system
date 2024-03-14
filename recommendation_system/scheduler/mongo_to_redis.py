from dao import redis_db
from dao.mongo_db import MongoDB


class mongo_to_redis(object):
    def __init__(self):
        self._redis = redis_db.Redis()
        self.mongo = MongoDB(db='recommendation')
        self.db_recommendation = self.mongo.db_recommendation
        self.collection_content = self.db_recommendation['content_label']

    def get_from_mongoDB(self):
        pipelines = [{
            '$group': {
                '_id': "$type"
            }
        }]
        types = self.collection_content.aggregate(pipelines)

        for type in types:
            collection = {"type": type['_id']}
            data = self.collection_content.find(collection)
            for info in data:
                result = dict()
                result_title = dict()
                result['content_id'] = str(info['_id'])
                result['describe'] = str(info['describe'])
                result['type'] = str(info['type'])
                result['title'] = str(info['title'])
                result['news_date'] = str(info['news_date'])
                result['likes'] = info['likes']
                result['read'] = info['read']
                result['hot_heat'] = info['hot_heat']
                result['collections'] = info['collections']

                result_title['content_id'] = str(info['_id'])
                result_title['title'] = str(info['title'])
                self._redis.redis.set("news_title:" + str(info['_id']), str(result))


if __name__ == '__main__':
    write_to_redis = mongo_to_redis()
    write_to_redis.get_from_mongoDB()
