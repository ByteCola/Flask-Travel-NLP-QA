class QuickSearcher(object):

    """
    对每个句子的词建立反向映射表，透过 set operator 快速限缩查询时间
    """

    def __init__(self, docs=None):

        self.inverted_word_dic = dict()
        #self.buildInvertedIndex(docs)

    def buildInvertedIndex(self, docs):

        """
        建构词对 ID 的倒排索引

        Args:
            - docs: 欲建构的倒排索引表列，每个 doc 需「完成断词」
        """

        for doc_id,doc in enumerate(docs):
            for word in doc:
                if word not in self.inverted_word_dic.keys():
                    self.inverted_word_dic[word] = set()
                self.inverted_word_dic[word].add(doc_id)

    def quickSearch(self, query):

        """
        读入已断好词的 query，依照倒排索引只取出必要的 id
        """

        result = set()
        # print(query)
        for word in query:
            if word in self.inverted_word_dic.keys():
                result = result.union(self.inverted_word_dic[word])

        return result
