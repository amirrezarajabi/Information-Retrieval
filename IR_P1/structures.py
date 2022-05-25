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