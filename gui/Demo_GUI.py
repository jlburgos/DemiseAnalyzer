#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys,time,string
sys.path.append("./demise_analyzer")

from DemiseAnalyzer import DemiseAnalyzer
from PyQt4 import QtGui


#class DemiseAnalyzerDemo(QtGui.QWidget):
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

  def process_query(self,text):
    text = reduce(lambda text,c: text.replace(c,''), string.punctuation, text)
    text = str(text).split()
    tmp = ''
    for word in text:
      tmp += '"'+word+'"+'
    return tmp[:-1]

  def show_dialog(self):
    self.statusBar().showMessage('Awaiting User Query ...')
    text, ok = QtGui.QInputDialog.getText(self, 'Provide Activity', 'User Activity:')
    self.statusBar().showMessage('Processing User Query...')
    #self.show()
    if ok and text != "":
      start_time = time.time()
      text = self.process_query(text)
      google_snippets = self.analyzer.online_search(num_bad_words=1,num_google_pages=1,activity_query=text)
      analyzer_output = self.analyzer.rocchio(self.MAX_SENTENCES)
      print "\n_____________________________________________________________\n"
      i = 0
      for result in analyzer_output:
        print i+1,')',result
        i+=1
      print "_____________________________________________________________\n"
      print "Rocchio_V1 with Naive Bayes info deems your activity: ",self.analyzer.danger_r1
      print "Rocchio_V2 with a database info deems your activity:  ",self.analyzer.danger_r2
      end_time = time.time()
      print 'done with constructing results after %.3f seconds'%(end_time-start_time)
      self.statusBar().showMessage('Ready for Action!')
    else:
      self.statusBar().showMessage('User entered empty string, waiting ...')


