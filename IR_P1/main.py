import json
from config import CONF
from structures import *
import pickle
import math
import numpy as np

conf = CONF()

DICTIONARY_INFO_DOC = {}
DICTIONARY = {}
N_TOKENS = 0

# T = []
# M = []

JSON = json.load(open(conf.DATA))
for doc in JSON:
    DICTIONARY_INFO_DOC[doc] = (JSON[doc][conf.TITLE], JSON[doc][conf.URL])
    tokens = conf.preprocess_content(JSON[doc][conf.CONTENT], conf.stopwords)
    for index, token in enumerate(tokens):
        if not token in DICTIONARY:
            DICTIONARY[token] = WORD(token)
        DICTIONARY[token].add_posting(doc, index)
        N_TOKENS += 1

#     if (doc == "499" or doc == "999" or doc == "1499" or doc == "1999"):
#         # save DICTIONARY length
#         M.append(math.log10(len(DICTIONARY)))
#         # save TOKEN length
#         T.append(math.log10(N_TOKENS))

# m, b = conf.bestline(T, M)
# print(f"log(k) = {m}, b = {b}, T = {N_TOKENS}, actual M = {len(DICTIONARY)}")
# # estimate the number of vocabulary
# estimated_vocabulary = math.pow(10, m * math.log10(N_TOKENS) + b)
# print(f"estimated number of vocabulary = {estimated_vocabulary}")
# conf.plot(T, M, "log(T)", "log(M)", "log(M) vs log(T)", flag=False, xp=T, yp=m * np.array(T) + b)


X = []
for token in DICTIONARY:
    X.append(DICTIONARY[token].doc_freq)
X = sorted(X)
X = X[::-1]
I = list(range(1, len(X) + 1))
for i in range(len(X)):
    I[i] = math.log10(I[i])
    X[i] = math.log10(X[i])
conf.plot(I, X, 'log(i)', 'log(f(i))', 'log(f(i)) vs log(i)')