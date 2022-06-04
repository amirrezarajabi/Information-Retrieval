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
    CHAMPIONS_LIST = "./saved/CHAMPION.rj"
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


from tkinter import *
from search_engine import SEARCH_ENGINE
import pyperclip

SE = SEARCH_ENGINE(Load=True, Save=False)

root = Tk()
root.title("RJ search engine")
root.geometry("800x400")
my_label_frame = LabelFrame(root, text="Search")
my_label_frame.pack(pady=20)
my_entry = Entry(my_label_frame, width=50)
my_entry.pack(pady=20, padx=20)

my_frame = Frame(root)
my_frame.pack(pady=20)

text_yscrollbar = Scrollbar(my_frame)
text_yscrollbar.pack(side=RIGHT, fill=Y)

text_xscrollbar = Scrollbar(my_frame, orient=HORIZONTAL)
text_xscrollbar.pack(side=BOTTOM, fill=X)

my_text = Text(my_frame, xscrollcommand=text_xscrollbar.set, yscrollcommand=text_yscrollbar.set, wrap=None)
my_text.pack(side=LEFT, fill=BOTH, expand=True)

text_xscrollbar.config(command=my_text.xview)
text_yscrollbar.config(command=my_text.yview)

butt_frame = Frame(root)
butt_frame.pack(pady=10)

def SEARCH():
    data = my_entry.get()
    my_text.delete(0.0, END)
    ans = SE.answer(data)
    DATA = []
    i = 0
    for s in ans:
        my_text.insert(END, str(i) + " - \n" + s)
        my_text.insert(END, "\n")
        my_text.insert(END, "---------------------------------------------\n")
        i += 1

def CLEAR():
    my_entry.delete(0, END)
    my_text.delete(0.0, END)

search_butt = Button(butt_frame, text="Search", command=SEARCH)
search_butt.grid(row=0, column=0, padx=10)
clear_butt = Button(butt_frame, text="Clear", command=CLEAR)
clear_butt.grid(row=0, column=1, padx=10)
copy_entry = Entry(butt_frame, width=50)
copy_entry.grid(row=0, column=2, padx=10)

def COPY():
    num = int(copy_entry.get())
    X = my_text.get(0.0, END)
    X = X.split("\n")
    if 4 * num + 3 < len(X):
        pyperclip.copy(X[4 * num + 2])
    del X

copy_butt = Button(butt_frame, text="Copy", command=COPY)
copy_butt.grid(row=0, column=3, padx=10)
root.mainloop()

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
                self.DICTIONARY_INFO_DOC[doc] = (JSON[doc][self.conf.TITLE], JSON[doc][self.conf.URL], len(tokens))
                for index, token in enumerate(tokens):
                    if not token in self.DICTIONARY:
                        self.DICTIONARY[token] = WORD(token)
                    self.DICTIONARY[token].add_posting(doc, index)
                    self.N_TOKENS += 1
            self.N = len(self.DICTIONARY_INFO_DOC)
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
        lenght_doc = {}
        for t in list(dic_q.keys()):
            tf_q, idf_q = self.calculate_tf_idf_query(t, dic_q)
            w_tq = tf_q * idf_q
            for docID in self.DICTIONARY[t].postingslist:
                tf, idf = self.calculate_tf_idf(docID, t)
                w_td = tf * idf
                if not docID in docs:
                    docs[docID] = [w_td * w_tq, 1]
                    lenght_doc[docID] = w_td ** 2
                else:
                    docs[docID][0] += w_td * w_tq
                    docs[docID][1] += 1
                    lenght_doc[docID] += w_td ** 2
                
        ans = []
        for docID in docs:
            if docs[docID][1] >= filter:
                docs[docID][0] = docs[docID][0] / math.sqrt(lenght_doc[docID])
                ans.append((docID, docs[docID]))
        ans.sort(key=lambda x: x[1][0], reverse=True)
        if len(ans) > k:
            ans = ans[:k]
        return ans


    def run_champions(self, query, k=20, filter=1):
        dic_q = self.prepare(query)
        docs = {}
        lenght_doc = {}
        for t in list(dic_q.keys()):
            tf_q, idf_q = self.calculate_tf_idf_query_champions(t, dic_q)
            w_tq = tf_q * idf_q
            for docID in self.champions_list[t][1]:
                tf, idf = self.calculate_tf_idf_champions(docID, t)
                w_td = tf * idf
                if not docID in docs:
                    docs[docID] = [w_td * w_tq, 1]
                    lenght_doc[docID] = w_td ** 2
                else:
                    docs[docID][0] += w_td * w_tq
                    docs[docID][1] += 1
                    lenght_doc[docID] += w_td ** 2
        ans = []
        for docID in docs:
            if docs[docID][1] >= filter:
                docs[docID][0] = docs[docID][0] / math.sqrt(lenght_doc[docID])
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
    
STOPWORDS = """
و
در
به
از
که
این
را
با
است
برای
آن
یک
خود
تا
کرد
بر
هم
نیز
.
،
؛
:
؟
!
>
>>
<
<<
(
)
وی
شد
دارد
ما
اما
یا
شده
باید
هر
آنها
بود
او
دیگر
"""

STOPWORDS2 = """و
در
به
از
که
این
را
با
است
برای
آن
یک
خود
تا
کرد
بر
هم
نیز
گفت
می‌شود
وی
شد
دارد
ما
اما
یا
شده
باید
هر
آنها
بود
او
دیگر
دو
مورد
می‌کند
شود
کند
وجود
بین
پیش
شده_است
پس
نظر
اگر
همه
یکی
حال
هستند
من
کنند
نیست
باشد
چه
بی
می
بخش
،
؛
:
؟
!
>
>>
<
<<
(
)
می‌کنند
همین
افزود
هایی
دارند
راه
همچنین
روی
داد
بیشتر
بسیار
سه
داشت
چند
سوی
تنها
هیچ
میان
اینکه
شدن
بعد
جدید
ولی
حتی
کردن
برخی
کردند
می‌دهد
اول
نه
کرده_است
نسبت
بیش
شما
چنین
طور
افراد
تمام
درباره
بار
بسیاری
می‌تواند
کرده
چون
ندارد
دوم
بزرگ
طی
حدود
همان
بدون
البته
آنان
می‌گوید
دیگری
خواهد_شد
کنیم
قابل
یعنی
رشد
می‌توان
وارد
کل
ویژه
قبل
براساس
نیاز
گذاری
هنوز
لازم
سازی
بوده_است
چرا
می‌شوند
وقتی
گرفت
کم
جای
حالی
تغییر
پیدا
اکنون
تحت
باعث
مدت
فقط
زیادی
تعداد
آیا
بیان
رو
شدند
عدم
کرده_اند
بودن
نوع
بلکه
جاری
دهد
برابر
مهم
بوده
اخیر
مربوط
امر
زیر
گیری
شاید
خصوص
آقای
اثر
کننده
بودند
فکر
کنار
اولین
سوم
سایر
کنید
ضمن
مانند
باز
می‌گیرد
ممکن
حل
دارای
پی
مثل
می‌رسد
اجرا
دور
منظور
کسی
موجب
طول
امکان
آنچه
تعیین
گفته
شوند
جمع
خیلی
علاوه
گونه
تاکنون
رسید
ساله
گرفته
شده_اند
علت
چهار
داشته_باشد
خواهد_بود
طرف
تهیه
تبدیل
مناسب
زیرا
مشخص
می‌توانند
نزدیک
جریان
روند
بنابراین
می‌دهند
یافت
نخستین
بالا
پنج
ریزی
عالی
چیزی
نخست
بیشتری
ترتیب
شده_بود
خاص
خوبی
خوب
شروع
فرد
کامل
غیر
می‌رود
دهند
آخرین
دادن
جدی
بهترین
شامل
گیرد
بخشی
باشند
تمامی
بهتر
داده_است
حد
نبود
کسانی
می‌کرد
داریم
می‌باشد
دانست
ناشی
داشتند
دهه
می‌شد
ایشان
آنجا
گرفته_است
دچار
می‌آید
لحاظ
آنکه
داده
بعضی
هستیم
اند
برداری
نباید
می‌کنیم
نشست
سهم
همیشه
آمد
اش
وگو
می‌کنم
حداقل
طبق
جا
خواهد_کرد
نوعی
چگونه
رفت
هنگام
فوق
روش
ندارند
سعی
بندی
شمار
کلی
کافی
مواجه
همچنان
زیاد
سمت
کوچک
داشته_است
چیز
پشت
آورد
حالا
روبه
سال‌های
دادند
می‌کردند
عهده
نیمه
جایی
دیگران
سی
بروز
یکدیگر
آمده_است
جز
کنم
سپس
کنندگان
خودش
همواره
یافته
شان
صرف
نمی‌شود
رسیدن
چهارم
یابد
متر
ساز
داشته
کرده_بود
باره
نحوه
کردم
تو
شخصی
داشته_باشند
محسوب
پخش
کمی
متفاوت
سراسر
کاملا
داشتن
نظیر
آمده
گروهی
فردی
ع
همچون
خطر
خویش
کدام
دسته
سبب
عین
آوری
متاسفانه
بیرون
دار
ابتدا
شش
افرادی
می‌گویند
سالهای
درون
نیستند
یافته_است
پر
خاطرنشان
گاه
جمعی
اغلب
دوباره
می‌یابد
لذا
زاده
گردد
اینجا
"""

import bisect

"""
poditional postings list class
"""

class DOCPOSITIONLIST:
    def __init__(self, docID):
        self.doc_id = docID
        self.positions = []
        self.freq = 0
    
    def add_position(self, position):
        bisect.insort(self.positions, position)
        self.freq += 1


"""
word class for the information retrieval project
"""

class WORD:
    def __init__(self, word):
        self.postingslist = {}
        self.doc_freq = 0
        self.total_freq = 0

    def add_posting(self, docID, position):
        if not docID in self.postingslist:
            self.postingslist[docID] = DOCPOSITIONLIST(docID)
            self.doc_freq += 1
        self.postingslist[docID].add_position(position)
        self.total_freq += 1
    


"""
example:
hi : (4, {56: (2, [1, 80]), 59: (1, [3]), 61: (1, [4])})
"""

from search_engine import SEARCH_ENGINE

print("Setting Up ...")
SE = SEARCH_ENGINE(Load=False, Save=True)

while True:
    data = input("Enter your query: ")
    if data == "exit":
        break
    ans = SE.answer(data)
    s = "\n".join(ans)
    print(s)

print("Bye!")

