import faiss
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from tensorflow.python.keras import Model
from models.recall.preprocess import gen_data_set, gen_model_input
from deepctr.feature_column import SparseFeat, VarLenSparseFeat
from tensorflow.python.keras import backend as K
import tensorflow as tf
from deepmatch.models import *
from deepmatch.utils import recall_N
from deepmatch.utils import sampledsoftmaxloss
import numpy as np
from tqdm import tqdm


class YoutubeModel(object):
    def __init__(self, embedding_dim=32):
        self.SEQ_LEN = 50
        self.embedding_dim = embedding_dim
        self.user_feature_columns = None
        self.item_feature_columns = None

    def training_set_construct(self):
        # Load data
        data = pd.read_csv('../../data/read_history.csv')
        # Number of negative samples
        negsample = 0
        # Feature encoding
        features = ["user_id", "item_id", "gender", "age", "city"]
        features_max_idx = {}
        for feature in features:
            lbe = LabelEncoder()
            data[feature] = lbe.fit_transform(data[feature]) + 1
            features_max_idx[feature] = data[feature].max() + 1

        # Extract user and item features
        user_info = data[["user_id", "gender", "age", "city"]].drop_duplicates('user_id')  # 去重操作
        item_info = data[["item_id"]].drop_duplicates('item_id')
        user_info.set_index("user_id", inplace=True)

        # Construct input data
        train_set, test_set = gen_data_set(data, negsample)
        # Convert to model input
        train_model_input, train_label = gen_model_input(train_set, user_info, self.SEQ_LEN)
        test_model_input, test_label = gen_model_input(test_set, user_info, self.SEQ_LEN)
        # User-side feature input
        self.user_feature_columns = [SparseFeat('user_id', features_max_idx['user_id'], 16),
                                     SparseFeat('gender', features_max_idx['gender'], 16),
                                     SparseFeat('age', features_max_idx['age'], 16),
                                     SparseFeat('city', features_max_idx['city'], 16),
                                     VarLenSparseFeat(SparseFeat('hist_item_id', features_max_idx['item_id'],
                                                                 self.embedding_dim, embedding_name='item_id'),
                                                      self.SEQ_LEN, 'mean', 'hist_len')
                                     ]
        # Item-side feature input
        self.item_feature_columns = [SparseFeat('item_id', features_max_idx['item_id'], self.embedding_dim)]

        return train_model_input, train_label, test_model_input, test_label, train_set, test_set, user_info, item_info

    def training_model(self, train_model_input, train_label):
        K.set_learning_phase(True)
        if tf.__version__ >= '2.0.0':
            tf.compat.v1.disable_eager_execution()
        # define model
        model = YoutubeDNN(self.user_feature_columns, self.item_feature_columns, num_sampled=100,
                           user_dnn_hidden_units=(128, 64, self.embedding_dim))
        model.compile(optimizer="adam", loss=sampledsoftmaxloss)
        # store data in the training process
        model.fit(train_model_input, train_label, batch_size=512, epochs=20, verbose=1, validation_split=0.0, )
        return model

    def extract_embedding_layer(self, model, test_model_input, item_info):
        all_item_model_input = {"item_id": item_info['item_id'].values, }
        # get user and item embedding_layer
        user_embedding_model = Model(inputs=model.user_input, outputs=model.user_embedding)
        item_embedding_model = Model(inputs=model.item_input, outputs=model.item_embedding)

        user_embs = user_embedding_model.predict(test_model_input, batch_size=2 ** 12)
        item_embs = item_embedding_model.predict(all_item_model_input, batch_size=2 ** 12)
        print(user_embs.shape)
        print(item_embs.shape)
        return user_embs, item_embs

    def eval(self, user_embs, item_embs, test_model_input, item_info, test_set):
        test_true_label = {line[0]: line[2] for line in test_set}
        index = faiss.IndexFlatIP(self.embedding_dim)
        index.add(item_embs)
        D, I = index.search(np.ascontiguousarray(user_embs), 50)
        s = []
        hit = 0

        # Statistical prediction results
        for i, uid in tqdm(enumerate(test_model_input['user_id'])):
            try:
                pred = [item_info['item_id'].value[x] for x in I[i]]
                recall_score = recall_N(test_true_label[uid], pred, N=50)
                s.append(recall_score)
                if test_true_label[uid] in pred:
                    hit += 1
            except:
                print(i)

        # Calculate recall and hit rate
        recall = np.mean(s)
        hit_rate = hit / len(test_model_input['user_id'])

        return recall, hit_rate

    def scheduler(self):
        # construct train and test dataset
        train_model_input, train_label, test_model_input, test_label, \
            train_set, test_set, user_info, item_info = self.training_set_construct()
        #
        self.training_model(train_model_input, train_label)

        # get user and item layer
        # user_embs, item_embs = self.extract_embedding_layer(model, test_model_input, item_info)
        # # evaluate model
        # recall, hit_rate = self.eval(user_embs, item_embs, test_model_input, item_info, test_set)
        # print(recall, hit_rate)


if __name__ == '__main__':
    model = YoutubeModel()
    model.scheduler()
