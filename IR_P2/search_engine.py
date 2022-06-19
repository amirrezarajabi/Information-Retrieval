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
        self.N = None
        self.champions_list = {}
        if Load:
            DICTIONARY_INFO_DOC_F = open(self.conf.DICTIONARY_INFO_DOC, 'rb')
            self.DICTIONARY_INFO_DOC = pickle.load(DICTIONARY_INFO_DOC_F)
            DICTIONARY_INFO_DOC_F.close()
            DICTIONARY_F = open(self.conf.DICTIONARY, 'rb')
            self.DICTIONARY = pickle.load(DICTIONARY_F)
            DICTIONARY_F.close()
            self.N = len(self.DICTIONARY_INFO_DOC)
            CHAMPIONS_LIST_F = open(self.conf.CHAMPIONS_LIST, 'rb')
            self.champions_list = pickle.load(CHAMPIONS_LIST_F)
            CHAMPIONS_LIST_F.close()
        else:
            self.DICTIONARY_INFO_DOC = {}
            self.DICTIONARY = {}
            self.N_TOKENS = 0
            JSON = json.load(open(self.conf.DATA))
            for doc in JSON:
                tokens = self.conf.preprocess_content(JSON[doc][self.conf.CONTENT], self.swords)
                self.DICTIONARY_INFO_DOC[doc] = [JSON[doc][self.conf.TITLE], JSON[doc][self.conf.URL], 0]
                for index, token in enumerate(tokens):
                    if not token in self.DICTIONARY:
                        self.DICTIONARY[token] = WORD(token)
                    self.DICTIONARY[token].add_posting(doc, index)
                    self.N_TOKENS += 1
            self.N = len(self.DICTIONARY_INFO_DOC)
            for t in self.DICTIONARY.keys():
                for docID in self.DICTIONARY[t].postingslist.keys():
                    self.DICTIONARY_INFO_DOC[docID][2] += self.doc_tf_idf(docID, t) ** 2
            self.create_champions_list()
            if Save:
                DICTIONARY_INFO_DOC_F = open(self.conf.DICTIONARY_INFO_DOC, 'wb')
                pickle.dump(self.DICTIONARY_INFO_DOC, DICTIONARY_INFO_DOC_F)
                DICTIONARY_INFO_DOC_F.close()

                DICTIONARY_F = open(self.conf.DICTIONARY, 'wb')
                pickle.dump(self.DICTIONARY, DICTIONARY_F)
                DICTIONARY_F.close()

                CHAMPIONS_LIST_F = open(self.conf.CHAMPIONS_LIST, 'wb')
                pickle.dump(self.champions_list, CHAMPIONS_LIST_F)
                CHAMPIONS_LIST_F.close()
    
    def calculate_tf_idf(self, docID, t):
        tf = 1 + math.log10(self.DICTIONARY[t].postingslist[docID].freq)
        idf = math.log10(self.N / self.DICTIONARY[t].doc_freq)
        return tf, idf
    
    def calculate_tf_idf_query(self, t, dic_q):
        tf = 1 + math.log10(dic_q[t])
        idf = math.log10(self.N / self.DICTIONARY[t].doc_freq)
        return tf, idf

    def doc_tf_idf(self, docID, t):
        tf, idf = self.calculate_tf_idf(docID, t)
        return tf * idf
    
    def calculate_tf_idf_champions(self, docID, t):
        tf = 1 + math.log10(self.champions_list[t][1][docID])
        idf = math.log10(self.N / self.champions_list[t][0])
        return tf, idf

    def calculate_tf_idf_query_champions(self, t, dic_q):
        tf = 1 + math.log10(dic_q[t])
        idf = math.log10(self.N / self.champions_list[t][0])
        return tf, idf
    
    def doc_tf_idf_champions(self, docID, t):
        tf, idf = self.calculate_tf_idf_champions(docID, t)
        return tf * idf
    
    def minimum_in_clist(self, clist, t):
        docs = list(clist.keys())
        min_doc = docs[0]
        min_score = self.doc_tf_idf(min_doc, t)
        for i in range(1, len(docs)):
            if min_score > self.doc_tf_idf(docs[i], t):
                min_doc = docs[i]
                min_score = self.doc_tf_idf(min_doc, t)
        return min_doc, min_score

    def create_champions_list(self, r=12000):
        for t in self.DICTIONARY:
            dis = list(self.DICTIONARY[t].postingslist.keys())
            self.champions_list[t] = [self.DICTIONARY[t].doc_freq, {}]
            if len(dis) <= r:
                for i in range(len(dis)):
                    self.champions_list[t][1][dis[i]] = self.DICTIONARY[t].postingslist[dis[i]].freq
            else:
                self.champions_list[t] = [self.DICTIONARY[t].doc_freq, {}]
                for i in range(r):
                    self.champions_list[t][1][dis[i]] = self.DICTIONARY[t].postingslist[dis[i]].freq
                min_doc, min_score = self.minimum_in_clist(self.champions_list[t][1], t)
                for i in range(r, len(dis)):
                    score = self.doc_tf_idf(dis[i], t)
                    if score > min_score:
                        self.champions_list[t][1][dis[i]] = self.DICTIONARY[t].postingslist[dis[i]].freq
                        del self.champions_list[t][1][min_doc]
                        min_doc, min_score = self.minimum_in_clist(self.champions_list[t][1], t)

    def prepare(self, query):
        q = self.conf.preprocess_content(query, self.swords)
        dic_q = {}
        for t in q:
            if not t in dic_q:
                dic_q[t] = 1
            else:
                dic_q[t] += 1
        return dic_q

    def run(self, query, k=20, filter=1):
        dic_q = self.prepare(query)
        print(dic_q)
        docs = {}
        for t in list(dic_q.keys()):
            tf_q, idf_q = self.calculate_tf_idf_query(t, dic_q)
            w_tq = tf_q * idf_q
            for docID in self.DICTIONARY[t].postingslist:
                tf, idf = self.calculate_tf_idf(docID, t)
                w_td = tf * idf
                if not docID in docs:
                    docs[docID] = [w_td * w_tq, 1]
                else:
                    docs[docID][0] += w_td * w_tq
                    docs[docID][1] += 1
                
        ans = []
        for docID in docs:
            if docs[docID][1] >= filter:
                docs[docID][0] = docs[docID][0] / math.sqrt(self.DICTIONARY_INFO_DOC[docID][2])
                ans.append((docID, docs[docID]))
        ans.sort(key=lambda x: x[1][0], reverse=True)
        if len(ans) > k:
            ans = ans[:k]
        return ans


    def run_champions(self, query, k=20, filter=1):
        dic_q = self.prepare(query)
        docs = {}
        for t in list(dic_q.keys()):
            tf_q, idf_q = self.calculate_tf_idf_query_champions(t, dic_q)
            w_tq = tf_q * idf_q
            for docID in self.champions_list[t][1]:
                tf, idf = self.calculate_tf_idf_champions(docID, t)
                w_td = tf * idf
                if not docID in docs:
                    docs[docID] = [w_td * w_tq, 1]
                else:
                    docs[docID][0] += w_td * w_tq
                    docs[docID][1] += 1
        ans = []
        for docID in docs:
            if docs[docID][1] >= filter:
                docs[docID][0] = docs[docID][0] / math.sqrt(self.DICTIONARY_INFO_DOC[docID][2])
                ans.append((docID, docs[docID]))
        ans.sort(key=lambda x: x[1][0], reverse=True)
        if len(ans) > k:
            ans = ans[:k]
        return ans
    
    def answer(self, query, k=20, filter=1):
        docs = self.run_champions(query, k, filter)
        for i in range(len(docs)):
            docs[i] = docs[i][0]
        S = []
        if docs == []:
            docs = "هیچ پاسخی برای شما پیدا نشد"
        if docs != "هیچ پاسخی برای شما پیدا نشد":
            for doc in docs:
                S.append(self.DICTIONARY_INFO_DOC[doc][0] + "\n" + self.DICTIONARY_INFO_DOC[doc][1])
        else: 
            S.append(docs)
        if (len(S) > 0):
            return S
        docs = self.run(query, k, filter)
        for i in range(len(docs)):
            docs[i] = docs[i][0]
        S = []
        if docs == []:
            docs = "هیچ پاسخی برای شما پیدا نشد"
        if docs != "هیچ پاسخی برای شما پیدا نشد":
            for doc in docs:
                S.append(self.DICTIONARY_INFO_DOC[doc][0] + "\n" + self.DICTIONARY_INFO_DOC[doc][1])
        else: 
            S.append(docs)
        return S