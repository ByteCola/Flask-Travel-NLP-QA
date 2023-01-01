# coding=utf-8

import logging
import pymongo

from .match import *


class Answerer(object):

    def __init__(self):

        self.general_questions = []
        self.path = os.path.dirname(__file__)

        self.matcher = getMatcher(matcherType="bm25", removeStopWords=True)
        self.fuzzy_matcher = getMatcher(matcherType="fuzzy", removeStopWords=True)
        # self.moduleTest()

        self.conn = pymongo.MongoClient(host="127.0.0.1", port=27017)
        self.db = self.conn['sight_qa_db']
        self.col_place = self.db.get_collection('place_data')
        self.col_sight = self.db.get_collection('sight_data')

    def moduleTest(self):

        logging.info("测试问答与断词模块中...")
        try:
            self.matcher.word_segmentation("测试一下断词")
            logging.info("测试成功")
        except Exception as e:
            logging.info(repr(e))
            logging.info("模块载入失败，请确认data与字典齐全")

    def get_response(self, sentence, algorithm="bm25"):
        response = self.get_general_qa(sentence, algorithm)
        return response

    def get_general_qa(self, query, algorithm, threshold=0):
        if algorithm == 'fuzzy':
            region, region_target, question_type = self.fuzzy_matcher.match(query)
        else:
            region, region_target, question_type = self.matcher.match(query)
        if not region or not region_target:
            return None, 0
        # matcher的返回修改为 领域分类（地市、景点）、地方（或景点）名称、问题分类、
        # region = 'sight'
        # question_type = 'address'
        # region_target = '石潭村'

        # sim = self.matcher.getSimilarity()
        sim = 1
        if sim < threshold:
            return None, 0
        else:
            reply = ''
            if region == 'sight':
                sight_data = self.col_sight.find_one({"name": region_target})
                if sight_data:
                    if question_type == 'sight_address':
                        reply = sight_data['address']
                    elif question_type == 'sight_telephone':
                        reply = sight_data['telephone']
                    else:
                        reply = sight_data['description']
            elif region == 'place':
                sight_list_data = self.col_sight.find({"place": region_target})

                for sight in sight_list_data:
                    reply += ( '<a href="'+sight["url"]+'" target="_blank">' + sight["name"] + '</a>&nbsp;')
            return reply, sim
