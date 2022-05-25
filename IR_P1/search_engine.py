import json
from config import CONF
from structures import *
import pickle
import math


class SEARCH_ENGINE:
    def __init__(self, Load=True, Save=False):
        self.conf = CONF()
        self.swords = self.conf.stopwords
        del self.swords["!"]
        if Load:
            DICTIONARY_INFO_DOC_F = open(self.conf.DICTIONARY_INFO_DOC, 'rb')
            self.DICTIONARY_INFO_DOC = pickle.load(DICTIONARY_INFO_DOC_F)
            DICTIONARY_INFO_DOC_F.close()
            DICTIONARY_F = open(self.conf.DICTIONARY, 'rb')
            self.DICTIONARY = pickle.load(DICTIONARY_F)
            DICTIONARY_F.close()
        else:
            self.DICTIONARY_INFO_DOC = {}
            self.DICTIONARY = {}
            self.N_TOKENS = 0
            JSON = json.load(open(self.conf.DATA))
            for doc in JSON:
                self.DICTIONARY_INFO_DOC[doc] = (JSON[doc][self.conf.TITLE], JSON[doc][self.conf.URL])
                tokens = self.conf.preprocess_content(JSON[doc][self.conf.CONTENT], self.swords)
                for index, token in enumerate(tokens):
                    if not token in self.DICTIONARY:
                        self.DICTIONARY[token] = WORD(token)
                    self.DICTIONARY[token].add_posting(doc, index)
                    self.N_TOKENS += 1
            if Save:
                DICTIONARY_INFO_DOC_F = open(self.conf.DICTIONARY_INFO_DOC, 'wb')
                pickle.dump(self.DICTIONARY_INFO_DOC, DICTIONARY_INFO_DOC_F)
                DICTIONARY_INFO_DOC_F.close()

                DICTIONARY_F = open(self.conf.DICTIONARY, 'wb')
                pickle.dump(self.DICTIONARY, DICTIONARY_F)
                DICTIONARY_F.close()
    
    def prepare(self, query):
        q = query.split('"')
        phrase = []
        Not = []
        for i in range(len(q) - 1, -1, -1):
            if i % 2 == 1:
                phrase.append(self.conf.preprocess_content(q[i], self.swords))
                q.remove(q[i])
        q = " ".join(q)
        qs = self.conf.preprocess_content(q, self.swords)
        for i in range (len(qs) - 1, -1, -1):
            if qs[i] == "!":
                del qs[i]
                continue
            if i - 1 >= 0:
                if qs[i - 1] == "!":
                    Not.append(qs[i])
                    del qs[i]
        for q in qs:
            if q == "":
                qs.remove(q)
        return qs, phrase, Not

    def answer_to_simple_query(self, query):
        ans = {}
        ANSs = []
        for q in query:
            if not q in self.DICTIONARY:
                return False
        for q in query:
            ANSs.append(self.query_doc_point(q))
        for i in range(len(ANSs)):
            for t in ANSs[i]:
                if not t in ans:
                    ans[t] = (1, ANSs[i][t])
                else:
                    ans[t] = (ans[t][0] + 1, ans[t][1] + ANSs[i][t])
        # sort dic by value[0] and then by value[1]
        tmp = sorted(ans.items(), key=lambda x: (x[1][0], x[1][1]), reverse=True)
        ans = {}
        for i in range(len(tmp)):
            ans[tmp[i][0]] = (tmp[i][1][0], tmp[i][1][1])
        k = 0
        for t in ans:
            if ans[t][0] == len(query):
                k += 1
            else:
                break
        return ans, k

    
    def answer_to_Not_query(self, query):
        for q in query:
            if not q in self.DICTIONARY:
                return False
        ans = []
        for i in range(len(self.DICTIONARY_INFO_DOC)):
            flag = True
            for q in query:
                if str(i) in self.DICTIONARY[q].postingslist:
                    flag = False
                    break
            if flag:
                ans.append(str(i))
        return ans

    def intersect(self, a, b):
        a = [int(x) for x in a]
        b = [int(x) for x in b]
        a.sort()
        b.sort()
        a = [str(x) for x in a]
        b = [str(x) for x in b]
        answer = []
        i, j = 0, 0
        while i < len(a) and j < len(b):
            if a[i] == b[j]:
                answer.append(a[i])
                i += 1
                j += 1
            elif int(a[i]) < int(b[j]):
                i += 1
            else:
                j += 1
        return answer
    
    def query_doc_point(self, q):
        docs = list(self.DICTIONARY[q].postingslist.keys())
        ans = {}
        for i in range(len(docs)):
            ans[docs[i]] = self.DICTIONARY[q].postingslist[docs[i]].freq
        return ans
    
    def answer_to_phrase_query(self, query):
        ans = set()
        q = query[0]
        if not q in self.DICTIONARY:
            return False
        LIST = self.DICTIONARY[q].postingslist
        for doc in list(LIST.keys()):
            for p in LIST[doc].positions:
                flag = True
                for i in range(1, len(query)):
                    if not doc in self.DICTIONARY[query[i]].postingslist:
                        flag = False
                        break
                    if not p + i in self.DICTIONARY[query[i]].postingslist[doc].positions:
                        flag = False
                        break
                if flag:
                    ans.add(doc)
        return list(ans)
    
    def phrase_answer(self, query):
        tmp = self.answer_to_phrase_query(query[0])
        for i in range(1, len(query)):
            tmp = self.intersect(tmp, self.answer_to_phrase_query(query[i]))
        return tmp

    def answer_to_query(self, query):
        qs, phrase, Not = self.prepare(query)
        ANS_NOT = None
        ANS_PHRASE = None
        ANS_SIMPLE = None
        if len(Not) > 0:
            ANS_NOT = self.answer_to_Not_query(Not)
        if len(phrase) > 0:
            ANS_PHRASE = self.phrase_answer(phrase)
        if len(qs) > 0:
            ANS_SIMPLE = self.answer_to_simple_query(qs)
        if ANS_NOT == False or ANS_PHRASE == False or ANS_SIMPLE == False:
            return "هیچ پاسخی برای شما پیدا نشد"
        if ANS_NOT is None and ANS_PHRASE is None and ANS_SIMPLE is None:
            return "هیچ پاسخی برای شما پیدا نشد"
        if ANS_NOT is None and ANS_PHRASE is None and ANS_SIMPLE is not None:
            return list(ANS_SIMPLE[0].keys())
        if ANS_NOT is None and ANS_PHRASE is not None and ANS_SIMPLE is None:
            return ANS_PHRASE
        if ANS_NOT is not None and ANS_PHRASE is None and ANS_SIMPLE is None:
            return ANS_NOT
        if ANS_NOT is not None and ANS_PHRASE is not None and ANS_SIMPLE is None:
            return self.intersect(ANS_NOT, ANS_PHRASE)
        if ANS_NOT is None and ANS_PHRASE is not None and ANS_SIMPLE is not None:
            return self.intersect(list(ANS_SIMPLE[0].keys())[:ANS_SIMPLE[1]], ANS_PHRASE)
        if ANS_NOT is not None and ANS_PHRASE is None and ANS_SIMPLE is not None:
            return self.intersect(ANS_NOT, list(ANS_SIMPLE[0].keys())[:ANS_SIMPLE[1]])
        if ANS_NOT is not None and ANS_PHRASE is not None and ANS_SIMPLE is not None:
            tmp = self.intersect(ANS_NOT, ANS_PHRASE)
            return self.intersect(tmp, list(ANS_SIMPLE[0].keys())[:ANS_SIMPLE[1]])
        return "هیچ پاسخی برای شما پیدا نشد"
    
    def answer(self, query):
        docs = self.answer_to_query(query)
        S = []
        if docs == []:
            docs = "هیچ پاسخی برای شما پیدا نشد"
        if docs != "هیچ پاسخی برای شما پیدا نشد":
            for doc in docs:
                S.append(self.DICTIONARY_INFO_DOC[doc][0] + "\n" + self.DICTIONARY_INFO_DOC[doc][1])
        else: 
            S.append(docs)
        return S
    