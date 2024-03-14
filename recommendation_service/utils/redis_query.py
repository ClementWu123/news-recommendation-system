from dao import redis_db


class RedisQuery:
    def __init__(self):
        self.redis_client = redis_db.Redis()

    def check_key_exist(self, key):
        return self.redis_client.redis.exists(key)


    def get_data_with_redis(self, user_id, page_num, page_size):
        redis_key = "rec_Item:" + str(user_id)
        if self.check_key_exist(redis_key):
            start_index = (page_num - 1) * page_size
            end_index = start_index + page_size - 1
            result = self.redis_client.redis.zrange(redis_key, start_index, end_index)

            lst = list()
            for x in result:
                info = self._redis.redis.get("news_detail:" + x)
                lst.append(info)
            return lst