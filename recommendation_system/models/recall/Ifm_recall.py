from tqdm import tqdm
from config.lfm_config import model_config
import numpy as np
import operator


class LFM_model(object):
    def __init__(self, train_file):
        """
        Training file, user vector, item vector
        :param train_file:
        """
        self.train_data = self.get_train_data(train_file)
        self.user_vec, self.item_vec = None, None

    def get_train_data(self, train_file):
        """
        Fetch data: [(user_id, score, item_id), ...]
        :param train_file:
        :return:
        """
        data = list()
        with open(train_file, mode='r', encoding='utf-8') as rf:
            for line in tqdm(rf.readlines()):
                user_id, score, itemid = line.strip().split(',')
                data.append([user_id, 1, itemid])
        return data

    def lfm_train(self):
        """
        Train the LFM (Latent Factor Model) algorithm
        :return: dict: key:user_id, value:np.ndarray {user_id:np.ndarray, ...}
                 dict: key:item_id, value:np.ndarray {item_id:np.ndarray, ...}
        """
        F, alpha, beta, step = model_config['F'], model_config['alpha'], model_config['beta'], model_config['step']
        user_vec, item_vec = {}, {}
        for s in range(step):
            print("this is the {}th step.".format(s + 1))
            for data_instance in tqdm(self.train_data):
                user_id, label, item_id = data_instance
                if user_id not in user_vec:
                    user_vec[user_id] = np.random.randn(F)
                if item_id not in item_vec:
                    item_vec[item_id] = np.random.randn(F)
                delta = label - self.model_predict(user_vec[user_id], item_vec[item_id])

                user_vec[user_id] += beta * (delta * item_vec[item_id] - alpha * user_vec[user_id])
                item_vec[item_id] += beta * (delta * user_vec[user_id] - alpha * item_vec[item_id])

            beta = beta * 0.9

        self.user_vec, self.item_vec = user_vec, item_vec

    def model_predict(self, user_vector, item_vector):
        """
        Calculate the distance between user_vec and item_vec

        :param user_vector:
        :param item_vector:
        :return:
        """
        res = np.dot(user_vector, item_vector) / (np.linalg.norm(user_vector) * np.linalg.norm(item_vector))
        return res

    def cal_rec_item(self, user_id):
        """
        Use the results of the LFM model to calculate the recommendation results
        :param user_id:
        :return: [(item_id, score),(item_id, score),(item_id, score) ...]
        """
        fix_num = model_config['fix_num']
        if user_id not in self.user_vec:
            return []
        record = dict()
        rec_list = list()
        user_vector = self.user_vec[user_id]
        for item_id in self.item_vec:
            item_vector = self.item_vec[item_id]
            res = self.model_predict(user_vector, item_vector)
            record[item_id] = res
        for items in sorted(record.items(), key=operator.itemgetter(1), reverse=True)[0:fix_num]:
            item_id = items[0]
            rec_list.append(item_id)
        return rec_list


if __name__ == '__main__':
    file = r"../../data/news_score/news_log.csv"
    lfm = LFM_model(file)
    lfm.lfm_train()

    rec_result = lfm.cal_rec_item('1')
    print(rec_result)