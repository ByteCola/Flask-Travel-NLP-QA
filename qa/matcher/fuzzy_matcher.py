import math
import os

from fuzzywuzzy import fuzz

from .matcher import Matcher


class FuzzyMatcher(Matcher):
    """
    基于莱文斯坦距离比对短语相似度
    """

    def __init__(self, removeStopWords=False):
        super().__init__()
        self.cleanStopWords = removeStopWords

        if removeStopWords:
            self.load_stop_words("data/stopwords/special_marks.txt")
            self.load_stop_words("data/stopwords/assist_wd.txt")

    def joinQuestions(self):
        self.seg_questions = ["".join(question) for question in self.seg_questions]


    def tieBreak(self, query, i, j):
        """
        当去除停用词后导致两个字串的匹配度一样时，从原文里挑选出更适合的

        Args:
            - query: 使用者的输入
            - i: index 为 i 的 title
            - j: index 为 j 的 title

        Return: (target, index)
            - target: 较适合的标题
            - index : 该标题的 id
        """
        raw1 = self.questions[i]
        raw2 = self.questions[j]

        r1 = fuzz.ratio(query, raw1)
        r2 = fuzz.ratio(query, raw2)

        if r1 > r2:
            return (raw1,i)
        else:
            return (raw2,j)

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

        ratio  = -1
        target = ""
        target_idx = -1

        if self.cleanStopWords:
            mQuery = [word for word in self.word_segmentation(query)
                      if word not in self.stopwords]
            mQuery = "".join(mQuery)
            question_list = self.seg_questions


        for index,question in enumerate(question_list):
            newRatio = fuzz.ratio(mQuery, question)

            if newRatio > ratio:
                ratio  = newRatio
                target = question
                target_idx = index

            elif self.cleanStopWords and newRatio == ratio:
                target, target_idx = self.tieBreak(query,target_idx,index)

        self.similarity = ratio


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

