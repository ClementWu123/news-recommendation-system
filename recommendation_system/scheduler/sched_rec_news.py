from read_data import read_news_data
from models.recall.Item_base_cf import ItemBaseCF
import pickle
from dao import redis_db


class SchedRecNews(object):
    def __init__(self):
        self.news_data = read_news_data.NewsData()
        self.Redis = redis_db.Redis()

    def schedule_job(self):
        """
        1. we need to determine who we want to recommend to, which means we need to calculate a list of users to
        recommend to. We can divide them into two categories: cold start users and users with recommendation history.
        We only need to calculate recommendations for users who have reading history.
        2. We train our model to obtain the collaborative filtering matrix.
        3. Make recommendations based on the model.
        4. Write the recommendation results to the database for later use.
        :return:
        """
        user_list = self.news_data.rec_user()
        # self.news_data.cal_score()
        self.news_model_train = ItemBaseCF("../data/news_score/news_log.csv")
        self.news_model_train.cf_item_train()
        # Model Serialization
        with open("../data/recall_model/CF_model/cf_news_recommend.m", mode='wb') as article_f:
            pickle.dump(self.news_model_train, article_f)
        for user_id in user_list:
            self.rec_list(user_id)

    def rec_list(self, user_id):
        recall_result = self.news_model_train.cal_rec_item(str(user_id))
        recall = []
        scores = []
        for item, score in recall_result.items():
            recall.append(item)
            scores.append(score)
        data = dict(zip(recall_result, scores))
        self.to_redis(user_id, data)
        print("item_cf to redis finish...")

    def to_redis(self, user_id, rec_conent_score):
        rec_item_id = "rec_item:" + str(user_id)
        res = dict()
        for content, score in rec_conent_score.items():
            res[content] = score

        if len(res) > 0:
            data = dict({rec_item_id: res})
            for item, value in data.items():
                self.Redis.redis.zadd(item, value)


if __name__ == '__main__':
    sched = SchedRecNews()
    sched.schedule_job()