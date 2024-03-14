from tqdm import tqdm
import numpy as np
import random
from keras_preprocessing.sequence import pad_sequences


def gen_data_set(data, negsample=0):
    data.sort_values("timestamp",
                     inplace=True)  # Whether to replace the original data with the sorted dataset, here it is replaced
    item_ids = data['item_id'].unique()  # Items need to be deduplicated

    train_set = list()
    test_set = list()
    for reviewrID, hist in tqdm(data.groupby('user_id')):  # Evaluated, historical record
        pos_list = hist['item_id'].tolist()
        rating_list = hist['rating'].tolist()

        if negsample > 0:  # Negative samples
            candidate_set = list(set(item_ids) - set(pos_list))  # Remove items that the user has already seen
            neg_list = np.random.choice(candidate_set, size=len(pos_list) * negsample,
                                        replace=True)  # Randomly select negative sampling
        for i in range(1, len(pos_list)):
            if i != len(pos_list) - 1:
                train_set.append(
                    (reviewrID, hist[::-1], pos_list[i], 1, len(hist[:: -1]),
                     rating_list[i]))  # Splitting training and testing sets [::-1] counts from the end to the front
                for negi in range(negsample):
                    train_set.append((reviewrID, hist[::-1], neg_list[i * negsample + negi], 0, len(hist[::-1])))
            else:
                test_set.append((reviewrID, hist[::-1], pos_list[i], 1, len(hist[::-1]), rating_list[i]))

    random.shuffle(train_set)  # Shuffle the dataset
    random.shuffle(test_set)
    return train_set, test_set


def gen_model_input(train_set, user_profile, seq_max_len):
    train_uid = np.array([line[0] for line in train_set])
    train_seq = [line[1] for line in train_set]
    train_iid = np.array([line[2] for line in train_set])
    train_label = np.array([line[3] for line in train_set])
    train_hist_len = np.array([line[4] for line in train_set])

    """
    pad_sequences data preprocessing
    sequences：A nested list consisting of floats or integers
    maxlen： None or an integer, representing the maximum length of the sequences. 
             Sequences longer than this length will be truncated, and those shorter will be padded with zeros at the end.
    dtype：The data type of the returned numpy array
    padding：‘pre’ or ‘post’， determines whether to pad zeros at the beginning or the end of the sequences when padding is needed
    truncating：‘pre’ or ‘post’，determines whether to truncate sequences from the beginning or the end when truncation is needed
    value：A float, this value will replace the default padding value of 0 when padding
    """
    train_seq_pad = pad_sequences(train_seq, maxlen=seq_max_len, padding='post', truncating='post', value=0)
    train_model_input = {"user_id": train_uid, "item_id": train_iid, "hist_item_id": train_seq_pad,
                         "hist_len": train_hist_len}
    for key in {"gender", "age", "city"}:
        train_model_input[key] = user_profile.loc[train_model_input['user_id']][key].values  # 训练模型的关键字

    return train_model_input, train_label
