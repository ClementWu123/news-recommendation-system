from dao.mongo_db import MongoDB
import os
import time


class NewsData(object):
    def __init__(self):
        self.mongo = MongoDB(db='recommendation')
        self.db_client = self.mongo.db_recommendation
        self.read_collection = self.db_client['read']
        self.likes_collection = self.db_client['likes']
        self.collection = self.db_client['collection']
        self.content = self.db_client['content_labels']

    """
    Read 1
    Like 2
    Favorite 3

    If both 2 and 3 exist, add 1 point.
    If both 2 and 3 exist simultaneously, add 2 points
    """
    def cal_score(self):
        result = list()
        score_dict = dict()
        data = self.likes_collection.find()
        for info in data:
            # The score calculation is done here
            score_dict.setdefault(info['user_id'], {})
            score_dict[info['user_id']].setdefault(info['content_id'], 0)

            query = {"user_id": info['user_id'], "content_id": info['content_id']}

            exist_count = 0
            # Query each table, and if data exists, add the corresponding score
            read_count = self.read_collection.find(query).count()
            if read_count > 0:
                score_dict[info['user_id']][info['content_id']] += 1
                exist_count += 1

            like_count = self.likes_collection.find(query).count()
            if like_count > 0:
                score_dict[info['user_id']][info['content_id']] += 2
                exist_count += 1

            collection_count = self.collection.find(query).count()
            if collection_count > 0:
                score_dict[info['user_id']][info['content_id']] += 2
                exist_count += 1

            if exist_count == 2:
                score_dict[info['user_id']][info['content_id']] += 1
            elif exist_count == 3:
                score_dict[info['user_id']][info['content_id']] += 2
            else:
                pass

            result.append(str(info['user_id']) + ',' + str(score_dict[info['user_id']][info['content_id']]) + ',' + str(info['content_id']))

        self.to_csv(result, '../data/news_score/news_log.csv')

    def rec_user(self):
        data = self.likes_collection.distinct('user_id')
        return data

    def to_csv(self, user_score_content, res_file):
        if not os.path.exists('../data/news_score'):
            os.mkdir('../data/news_score')
        with open(res_file, mode='w', encoding='utf-8') as wf:
            # info = "1,8,6145ec828451a2b8577df7b3"
            for info in user_score_content:
                wf.write(info + '\n')

        # print(len(user_score_content))


if __name__ == '__main__':
    news_data = NewsData()
    data = news_data.rec_user()
    print(data)