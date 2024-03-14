import redis


class Redis(object):
    def __init__(self):
        self.redis = redis.StrictRedis(host='localhost',
                                       port=6379,
                                       db=0,
                                       password='',
                                       decode_responses=True)