import logging
import os

import ahocorasick
import jieba

from database import Database


class Matcher(object):
    """
    比对使用者输入的句子与目标语料集，
    回传语料集中最相似的一个句子。
    """

    def __init__(self):

        logging.basicConfig(format='%(asctime)s : %(threadName)s : %(levelname)s : %(message)s', level=logging.INFO)
        self.questions = []  # 欲进行匹配的所有问题
        self.seg_questions = []  # 断好词的问题
        self.all_places = []  # 所有地点信息
        self.all_sights = []  # 所有景点信息
        self.place_domain_dicts = []  # 地点字典
        self.sight_domain_dicts = []  # 景点字典

        self.stopwords = set()
        self.similarity = 1.
        self.load_all_sights()

    def load_stop_words(self, path):
        with open(path, 'r', encoding='utf-8') as sw:
            for word in sw:
                self.stopwords.add(word.strip('\n'))

    def load_places(self, path):
        with open(path, 'r', encoding='utf-8') as data:
            self.all_places = [line.strip('\n') for line in data]

    def load_questions(self, path):

        with open(path, 'r', encoding='utf-8') as data:
            self.questions = [line.strip('\n') for line in data]

    def build_place_domain_dicts(self, segQuestion):
        # 地点领域词汇查询
        for qwd in segQuestion:
            if qwd in self.all_places:
                self.place_domain_dicts.append({qwd: "place"})

    def build_sight_domain_dicts(self, segQuestion):
        if len(self.all_sights) == 0:
            self.load_all_sights()
        for qwd in segQuestion:
            if qwd in self.all_sights:
                self.sight_domain_dicts.append({qwd: "sight"})

    def load_all_sights(self):
        database = Database()
        sight_col = database.get_collection("sight_qa_db", "sight_data")
        ##################################### codee
        sight_data_list = list(sight_col.find())
        for sight_object in sight_data_list:
            self.all_sights.append(sight_object["name"])

    '''构造actree，加速过滤'''

    def build_actree(self, wordlist):
        actree = ahocorasick.Automaton()
        for index, word in enumerate(wordlist):
            actree.add_word(word, (index, word))
        actree.make_automaton()
        return actree

    def match(self, query):

        """
        读入使用者 query，若语料库中存在相同的句子，便回传该句子与标号

        Args:
            - query: 使用者的输入

        Return: (question,index)
            - question: 最为相似的问题
            - 该问题的索引编号
        """

        result = None
        for index, question in enumerate(self.questions):
            if question == query:
                return question, index

    def getSimilarity(self):

        return self.similarity

    def loadCustomDict(self, path):
        # 自定义景点字典
        jieba.load_userdict(path)

    def word_segmentation(self, string):
        return [word for word in jieba.cut(string, cut_all=True)]

    def questions_segmentation(self, cleanStopwords=False):

        """
        将 self.questions 断词后的结果输出，并储存于 self.seg_questions

        Args:
            - cleanStopwords: 是否要清除问题中的停用词
        """

        logging.info("正准备将 questions 断词")

        count = 0

        if not os.path.exists('data/seg_questions.txt'):

            self.seg_questions = []
            for question in self.questions:

                if cleanStopwords:
                    clean = [word for word in self.word_segmentation(question)
                             if word not in self.stopwords]
                    self.seg_questions.append(clean)
                else:
                    self.seg_questions.append(self.word_segmentation(question))

                count += 1
                if count % 1000 == 0:
                    logging.info("已断词完前 %d 句" % count)

            with open('data/seg_questions.txt', 'w', encoding="utf-8") as seg_question:
                for question in self.seg_questions:
                    seg_question.write(' '.join(question) + '\n')
            logging.info("完成问题断词，结果已暂存至 data/seg_questions.txt")
        else:
            logging.info("侦测到先前的问题断词结果，读取中...")
            with open('data/seg_questions.txt', 'r', encoding="utf-8") as seg_question:
                for line in seg_question:
                    line = line.strip('\n')
                    seg = line.split()

                    if cleanStopwords:
                        seg = [word for word in seg
                               if word not in self.stopwords]
                    self.seg_questions.append(seg)
                logging.info("%d 个问题已完成载入" % len(self.seg_questions))
