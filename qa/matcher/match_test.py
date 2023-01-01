from qa.matcher.bm25_matcher import BestMatchingMatcher

if __name__=="__main__":
    bm25Matcher = BestMatchingMatcher()
    bm25Matcher.load_questions(path="../data/questions.txt")

    bm25Matcher.initialize()
    bm25Matcher.match(query="合肥有什么好玩的地方")


