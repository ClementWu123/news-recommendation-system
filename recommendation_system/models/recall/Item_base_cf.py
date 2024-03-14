from tqdm import tqdm
import math
import time


class ItemBaseCF(object):
    def __init__(self, train_file):
        """
        Reading files
        User and item history
        Item similarity calculation
        Training
        """
        self.train = dict()
        self.user_item_history = dict()
        self.item_to_item = dict()
        self.read_data(train_file)

    def read_data(self, train_file):
        """
        Read file and generate dataset (user, score, news item; represented as user, score, item)
        :param train_file: training file
        :return: {"user_id":{"content_id":predict_score}}
        """
        with open(train_file, mode='r', encoding='utf-8') as rf:
            for line in tqdm(rf.readlines()):
                user, score, item = line.strip().split(",")
                self.train.setdefault(user, {})
                self.user_item_history.setdefault(user, [])
                self.train[user][item] = int(score)
                self.user_item_history[user].append(item)

    def cf_item_train(self):
        """
        :return: similarity matrix：{content_id:{content_id:score}}
        """
        print("start train")
        self.item_to_item, self.item_count = dict(), dict()

        for user, items in self.train.items():
            for i in items.keys():
                self.item_count.setdefault(i, 0)
                self.item_count[i] += 1  # item i occur once, add 1

        for user, items in self.train.items():
            for i in items.keys():
                self.item_to_item.setdefault(i, {})
                for j in items.keys():
                    if i == j:
                        continue
                    self.item_to_item[i].setdefault(j, 0)
                    self.item_to_item[i][j] += 1 / (
                        math.sqrt(self.item_count[i] + self.item_count[j]))  # If item i and j appear together once, add 1

        # calculate similarity matrix
        for _item in self.item_to_item:
            self.item_to_item[_item] = dict(sorted(self.item_to_item[_item].items(),
                                                   key=lambda x: x[1], reverse=True)[0:30])

    def cal_rec_item(self, user, N=5):
        """
        Recommend the top N articles of interest to a user
        :param user:
        :param N:
        :return:  List of recommended articles
        """
        rank = dict()
        try:
            action_item = self.train[user]
            for item, score in action_item.items():
                for j, wj in self.item_to_item[item].items():
                    if j in action_item.keys():  # If article j has already been read, then it will not be recommended
                        continue
                    rank.setdefault(j, 0)
                    rank[j] += score * wj / 10000

            res = dict(sorted(rank.items(), key=lambda x: x[1], reverse=True)[0:N])
            print(res)
            return res

        except:
            return {}
