import math
import os

from .matcher import Matcher
from .quick_search import QuickSearcher


class BestMatchingMatcher(Matcher):
    """
    基于 bm25 算法取得最佳关联短语
    """

    def __init__(self, removeStopWords=False):
        super().__init__()
        self.cleanStopWords = removeStopWords
        self.D = 0  # 句子总数

        self.wordset = set()  # Corpus 中所有词的集合
        self.words_location_record = dict()  # 纪录该词 (key) 出现在哪几个句子(id)
        self.words_idf = dict()  # 纪录每个词的 idf 值

        self.f = []
        self.df = {}
        self.idf = {}
        self.k1 = 1.5
        self.b = 0.75

        self.searcher = QuickSearcher()  # 问句筛选

        if removeStopWords:
            self.load_stop_words("data/stopwords/special_marks.txt")
            self.load_stop_words("data/stopwords/assist_wd.txt")

    def initialize(self, ngram=1):

        assert len(self.questions) > 0, "请先载入问题列表"

        self.questions_segmentation()  # 将 self.questions 断词为  self.seg_questions
        # self.calculateIDF() # 依照断词后结果, 计算每个词的 idf value
        self.initBM25()
        self.searcher.buildInvertedIndex(self.seg_questions)

        """NEED MORE DISCUSSION
        #for n in range(0,ngram):
        #    self.addNgram(n)
        """

    def initBM25(self):

        print("BM25模块初始化中")

        self.D = len(self.seg_questions)
        self.avgdl = sum([len(question) + 0.0 for question in self.seg_questions]) / self.D

        for seg_title in self.seg_questions:
            tmp = {}
            for word in seg_title:
                if not word in tmp:
                    tmp[word] = 0
                tmp[word] += 1
            self.f.append(tmp)
            for k, v in tmp.items():
                if k not in self.df:
                    self.df[k] = 0
                self.df[k] += 1
        for k, v in self.df.items():
            self.idf[k] = math.log(self.D - v + 0.5) - math.log(v + 0.5)

        print("BM25模块初始化完成")

    def sim(self, doc, index):
        score = 0
        for word in doc:
            if word not in self.f[index]:
                continue
            d = len(self.seg_questions[index])
            score += (self.idf[word] * self.f[index][word] * (self.k1 + 1)
                      / (self.f[index][word] + self.k1 * (1 - self.b + self.b * d
                                                          / self.avgdl)))
        return score

    def calculateIDF(self):

        # 构建词集与纪录词出现位置的字典
        if len(self.wordset) == 0:
            self.buildWordSet()
        if len(self.words_location_record) == 0:
            self.buildWordLocationRecord()

        # 计算 idf
        for word in self.wordset:
            self.words_idf[word] = math.log2((self.D + .5) / (self.words_location_record[word] + .5))

    def buildWordLocationRecord(self):
        """
        建构词与词出现位置（句子id）的字典
        """
        for idx, seg_title in enumerate(self.seg_questions):
            for word in seg_title:
                if self.words_location_record[word] is None:
                    self.words_location_record[word] = set()
                self.words_location_record[word].add(idx)

    def buildWordSet(self):
        """
        建立 Corpus 词集
        """
        for seg_title in self.seg_questions:
            for word in seg_title:
                self.wordset.add(word)

    def addNgram(self, n):
        """
        扩充 self.seg_titles 为 n-gram
        """
        idx = 0

        for seg_list in self.seg_questions:
            ngram = self.generateNgram(n, self.questions[idx])
            seg_list = seg_list + ngram
            idx += 1

    def generateNgram(self, n, sentence):
        return [sentence[i:i + n] for i in range(0, len(sentence) - 1)]

    def joinQuestions(self):
        self.seg_questions = ["".join(question) for question in self.seg_questions]

    def match(self, query):
        """
        读入使用者 query，若语料库中存在类似的句子，便回传该句子与标号

        Args:
            - query: 使用者欲查询的语句
        """

        seg_query = self.word_segmentation(query)

        # 查询地点信息
        self.build_place_domain_dicts(seg_query)
        # 过滤地点（非景点同名）词汇
        for r in self.place_domain_dicts:
            for index, value in r.items():
                if index != '黄山':
                    seg_query.remove(index)
        # 查询景点信息
        self.build_sight_domain_dicts(seg_query)

        if len(self.place_domain_dicts) == 0 and len(self.sight_domain_dicts) == 0:
            return None, None, None

        max = -1
        target = ''
        target_idx = -1

        target_index = self.searcher.quickSearch(seg_query)  # 只取出必要的 questions

        for index in target_index:
            score = self.sim(seg_query, index)
            if score > max:
                target_idx = index
                max = score

        # normalization
        max = max / self.sim(self.seg_questions[target_idx], target_idx)
        target = ''.join(self.seg_questions[target_idx])
        self.similarity = max * 100  # 百分制

        # question = self.seg_questions[target_idx]

        question = self.questions[target_idx]

        question_items = question.split("|")

        # 确认最终查询的对象
        region = question_items[0]
        question_type = question_items[1]
        if region == "sight":
            region_target = list((self.sight_domain_dicts[0]).keys())[0]
        else:
            region_target = list((self.place_domain_dicts[0]).keys())[0]

        # return "sight", "sight_address", "黄山风景区"
        return region, region_target, question_type


