import json
import os
import random

from .matcher.bm25_matcher import BestMatchingMatcher
from .matcher.fuzzy_matcher import FuzzyMatcher


def getMatcher(matcherType, removeStopWords=False):
    """
    回传初始完毕的 matcher

    Args:
        - matcherType:要使用哪种字串匹配方式
            - Fuzzy
            - bm25
    """
    if matcherType == "bm25":
        return bm25()
    elif matcherType == "fuzzy":
        return fuzzyMatch()
    else:
        print("[Error]: Invailded type.")
        exit()


def matcherTesting(matcherType, removeStopWords=False):
    matcher = getMatcher(matcherType, removeStopWords)
    cur_path = os.path.dirname(__file__)

    while True:
        query = input("随便说些什么吧: ")
        title, index = matcher.match(query)
        sim = matcher.getSimilarity()
        print("最为相似的问题是 %s ，相似度为 %d " % (title, sim))


def fuzzyMatch():
    cur_dir = os.getcwd()
    os.chdir(os.path.dirname(__file__))
    fuzzyMatcher = FuzzyMatcher(removeStopWords=True)
    fuzzyMatcher.load_questions(path="data/questions.txt")

    fuzzyMatcher.load_places(path="data/dict/place.txt")
    fuzzyMatcher.loadCustomDict(path="data/dict/custom_wd.txt")

    fuzzyMatcher.questions_segmentation(True)
    fuzzyMatcher.joinQuestions()
    os.chdir(cur_dir)

    return fuzzyMatcher


def bm25():
    cur_dir = os.getcwd()
    os.chdir(os.path.dirname(__file__))
    bm25Matcher = BestMatchingMatcher()
    bm25Matcher.load_questions(path="data/questions.txt")
    bm25Matcher.load_places(path="data/dict/place.txt")
    bm25Matcher.loadCustomDict(path="data/dict/custom_wd.txt")
    # # 自定义景点字典
    # jieba.load_userdict(r"data/dict/custom_wd.txt")
    bm25Matcher.initialize()
    os.chdir(cur_dir)

    return bm25Matcher
