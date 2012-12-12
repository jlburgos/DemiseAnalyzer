# Source: http://www.tutorialspoint.com/python/python_multithreading.htm

import threading
import time
import nltk

class myThread(threading.Thread):
    def __init__(self, threadID, total_num_threads, tokenized_sentences):
        self.threadID = threadID
        self.total_num_threads = total_num_threads
        self.tokenized_sentences = tokenized_sentences
        threading.Thread.__init__(self)
        self.results = []

    def run(self):
        sz = len(self.tokenized_sentences)
        p = self.threadID
        q = self.total_num_threads
        self.results = [nltk.pos_tag(sent) for sent in self.tokenized_sentences[(p-1)*sz/q:p*sz/q]]

