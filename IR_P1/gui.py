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