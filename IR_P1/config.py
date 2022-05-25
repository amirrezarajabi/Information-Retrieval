from parsivar import FindStems
import hazm
import matplotlib.pyplot as plt
import numpy as np
from stopwords import STOPWORDS, STOPWORDS2

class CONF:
    TITLE = 'title'
    CONTENT = 'content'
    TAGS = 'tags'
    DATE = 'date'
    URL = 'url'
    CATEGORY = 'category'
    DATA = './data/IR_data_news_12k.json'
    MY_NORMALIZER = hazm.Normalizer()
    MY_STEMMER = FindStems()
    DICTIONARY_INFO_DOC = "./saved/DICTIONARY_INFO_DOC.rj"
    DICTIONARY = "./saved/DICTIONARY.rj"
    stopwords = {}
    for word in STOPWORDS.split('\n'):
        stopwords[word] = True

    def __init__(self):
        pass

    def preprocess_content(self, content, stopwords={}):
        normalized = self.MY_NORMALIZER.normalize(content)
        tokenized = hazm.word_tokenize(normalized)
        # stemmed = tokenized
        stemmed = [self.MY_STEMMER.convert_to_stem(token) for token in tokenized]
        for token in stemmed:
            if token in stopwords:
                stemmed.remove(token)
        return stemmed
    
    def plot(self, x, y, x_label, y_label, title, flag=True, xp=None, yp=None):
        import matplotlib.pyplot as plt
        plt.plot(x, y)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        if flag:
            m, b = self.bestline(x, y)
            plt.title(title + f" (k = {np.power(10, b)}, m = {m})")
            plt.plot(np.array(x), m * np.array(x) + b)
        else:
            plt.title(title)
        if xp is not None and yp is not None:
            plt.plot(xp, yp)
        plt.show()
    
    def bestfiteline(self, x, y):
        mean_x = np.mean(np.array(x))
        mean_y = np.mean(np.array(y))
        return mean_x + mean_y
    
    def bestline(self, x, y):
        mean_x = 0
        mean_y = 0
        mean_xy = 0
        mean_xx = 0
        for i in range(len(x)):
            mean_x += x[i]
            mean_y += y[i]
            mean_xy += x[i] * y[i]
            mean_xx += x[i] * x[i]
        mean_x, mean_y, mean_xy, mean_xx = mean_x / len(x), mean_y / len(x), mean_xy / len(x), mean_xx / len(x)
        m = (mean_xy - mean_x * mean_y) / (mean_xx - mean_x * mean_x)
        b = mean_y - m * mean_x
        return m, b