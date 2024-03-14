import os
import jieba
import jieba.posseg as pseg
import re
import jieba.analyse


class Segment(object):
    def __init__(self, stopword_files=[], userdict_files=[], jieba_tmp_dir=None):
        # temporary files of jieba segmentation
        if jieba_tmp_dir:
            jieba.dt.tmp_dir = jieba_tmp_dir
            # If it does not exist, create it
            if not os.path.exists(jieba_tmp_dir):
                os.makedirs(jieba_tmp_dir)

        self.stopwords = set()
        # The stop words file is already prepared
        for stopword_file in stopword_files:
            with open(stopword_file, "r", encoding="utf-8") as rf:
                for row in rf.readlines():
                    word = row.strip()
                    if len(word) > 0:
                        # Add the stop words file to the stop words list
                        self.stopwords.add(word)

        for userdict in userdict_files:
            # jieba loading user dictionary
            jieba.load_userdict(userdict)

    def cut(self, text):
        word_list = []
        # New line, full-width whitespace, non-breaking space
        text.replace('\n', '').replace('\u3000', '').replace('\u00A0', '')
        # Remove all special characters, punctuation, and spaces from a string
        text = re.sub('[a-zA-Z0-9.。:：,，]', '', text)
        # Use jieba tool for word segmentation
        words = pseg.cut(text)

        for word in words:
            # Part-of-speech tagging 'n', 'nr', 'ns', 'vn', 'v'
            print(word.word, word.flag)
            word = word.strip()
            # Remove some stop words and words with a length of 0
            if word in self.stopwords or len(word) == 0:
                continue
            word_list.append(word)

        return word_list  # 返回词典

    # Keyword extraction
    def extract_keyword(self, text, algorithm='tfidf', use_pos=True):
        # Remove all special characters, punctuation, and spaces from a string
        text = re.sub('[a-zA-Z0-9.。:：,，]', '', text)
        if use_pos:
            allow_pos = ('n', 'nr', 'ns', 'vn', 'v')  # Keyword part of speech
        else:
            allow_pos = ()

        # Keyword extraction algorithm based on TF-IDF or TextRank algorithm
        if algorithm == 'tfidf':
            # jieba extract keywords, withWeight determines whether to return the weight of each keyword
            tags = jieba.analyse.extract_tags(text, withWeight=True)
            return tags
        elif algorithm == 'textrank':
            # allowPOS specifies the allowed part-of-speech tags for extraction,
            # defaulting to allowPOS=('ns', 'n', 'vn', 'v'),
            # to extract place names, nouns, gerunds, and verbs
            textrank = jieba.analyse.textrank(text, withWeight=True,
                                              allowPOS=allow_pos)
            return textrank

    def combined_keyword(self, text, num):
        textrank = dict(self.extract_keyword(text, algorithm='textrank', use_pos=True))
        tfidfs = dict(self.extract_keyword(text, algorithm='tfidf', use_pos=True))

        # Identify common keywords
        common_keywords = set(tfidfs.keys()) & set(textrank.keys())

        # Combine weights for common keywords and calculate the average
        combined_keywords_weights = [(keyword, (float(tfidfs[keyword]) + float(textrank[keyword])) / 2) for keyword in
                                     common_keywords]

        # Sort the combined list by weight in descending order
        combined_keywords_weights_sorted = sorted(combined_keywords_weights, key=lambda x: x[1], reverse=True)

        # Select the top-K keywords based on their combined weights
        topk_combined_keywords_weights = combined_keywords_weights_sorted[:num]

        return topk_combined_keywords_weights


if __name__ == '__main__':
    seg = Segment(stopword_files=[], userdict_files=[])
    text = ("孙新军介绍，北京的垃圾处理能力相对比较宽松，全市有44座处理设施，总设计能力是每天处理3.2万吨，焚烧场11座，处理能力是1.67万吨每天，生化设施23座，日处理能力达8130"
            "吨，包括餐饮单位厨余垃圾日处理能力2380吨，家庭厨余垃圾日处理能力5750吨。")
    textrank = seg.extract_keyword(text, algorithm='textrank', use_pos=True)[:10]
    tfidfs = seg.extract_keyword(text, algorithm='tfidf', use_pos=True)[:10]
    result_textrank = []
    result_tfidf = []
    for i in textrank:
        result_textrank.append(i[0])
    for i in tfidfs:
        result_tfidf.append(i[0])
    print(result_textrank)
    print(result_tfidf)
    print(set(result_textrank) & set(result_tfidf))
