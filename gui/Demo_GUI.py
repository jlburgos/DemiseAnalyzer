#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import time
import string
sys.path.append("./demise_analyzer")

from DemiseAnalyzer import DemiseAnalyzer
from PyQt4 import QtGui


# class DemiseAnalyzerDemo(QtGui.QWidget):
class DemiseAnalyzerDemo(QtGui.QMainWindow):
    def __init__(self):
        super(DemiseAnalyzerDemo, self).__init__()
        self.initUI()

    def initUI(self):
        # Beginning Message
        print 'Launching Demise Analyzer Application ...'
        self.MAX_SENTENCES = 3000

        # Button to control Dialog Box
        self.btn = QtGui.QPushButton('Click Me!', self)
        self.btn.move(20, 20)
        self.btn.setToolTip('Click this button to provide an activity query.')
        self.btn.clicked.connect(self.show_dialog)

        # Configure Window
        self.setGeometry(300, 300, 400, 250)
        self.setWindowTitle('Demise Analyzer Demo Application')
        self.setWindowIcon(QtGui.QIcon('./img/trollface.png'))
        self.show()

        # Configure DemiseAnalyzer
        self.analyzer = DemiseAnalyzer()
        self.statusBar().showMessage('Ready for Action!')

        # End Message
        print 'Application ready for action!'

    def process_query(self, text):
        """
        Turn input string to form: "token"+"token"+ ... +"token"+token" for google custom search.
        """
        text = reduce(
            lambda text, c: text.replace(c, ''), string.punctuation, text)
        text = str(text).split()
        tmp = ''
        for word in text:
            tmp += '"' + word + '"+'
        return tmp[:-1]  # Return everything except the last '+' character

    def print_results(self, text):
        start_time = time.time()
        text = self.process_query(text)
        google_snippets = self.analyzer.online_search(
            num_bad_words=1, num_google_pages=1, activity_query=text)
        analyzer_output = self.analyzer.rocchio(self.MAX_SENTENCES)
        print "_____________________________________________________________"
        print "According to our trained Demise Analyzer Model, the top results are:"
        print "_____________________________________________________________"
        i = 0
        for result in analyzer_output:
            print i + 1, result[0]
            max_char = min(100, len(result[2]))
            print '--Sampled Sentence: %s ...' % result[2][:max_char]
            print '--------------------------------------------------------------'
            i += 1
        print "_____________________________________________________________"
        print "Rocchio with Naive Bayes info deems your activity:", self.analyzer.danger_r1
        end_time = time.time()
        print 'done with constructing results after %.3f seconds' % (end_time - start_time)
        print "_____________________________________________________________"

    def show_dialog(self):
        self.statusBar().showMessage('Awaiting User Query ...')
        text, ok = QtGui.QInputDialog.getText(
            self, 'Provide Activity', 'User Activity:')
        self.statusBar().showMessage('Processing User Query...')
        time.sleep(1)
        # self.show()
        if ok and text != "":
            self.print_results(text)
            self.statusBar().showMessage('Ready for Action!')
        else:
            self.statusBar(
            ).showMessage('User entered empty string, waiting ...')
