from dao import redis_db


class page_utils(object):
    def __init__(self):
        self._redis = redis_db.Redis()

    def get_data_with_page(self, page, page_size):
        start = (page - 1) * page_size
        end = start + page_size
        data = self._redis.redis.zrevrange("rec_date_list", start, end)
        lst = list()
        for x in data:
            info = self._redis.redis.get("news_detail:" + x)
            lst.append(info)
        return lst


if __name__ == '__main__':
    page_size = page_utils()
    print(page_size.get_data_with_page(1, 20))