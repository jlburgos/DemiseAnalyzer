#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
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
    print 'Loading Demise Analyzer Application...'

    # Button to control Dialog Box
    self.btn = QtGui.QPushButton('Click Me!', self)
    self.btn.move(20, 20)
    self.btn.setToolTip('Click this button to provide an activity query.')
    self.btn.clicked.connect(self.showDialog)

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

  def showDialog(self):
    self.statusBar().showMessage('Awaiting User Query...')
    text, ok = QtGui.QInputDialog.getText(self, 'Provide Activity', 'User Activity:')
    #self.show()
    if ok and text != "":
      self.statusBar().showMessage('Processing User Query...')
      #google_results = self.analyzer.online_search(num_bad_words=1,num_google_pages=1,activity_query=text)
      analyzer_output = self.analyzer.rocchio(3000)
      #analyzer_output = self.analyzer.createResults(google_results)

      print "\n_____________________________________________________________\n"
      print "Nouns:"
      for i in xrange(len(analyzer_output[0])):
        print i+1,') ',analyzer_output[0][i]
        if i+1 > 10: break
      print "When doing this activity you are most likely to: "
      for i in xrange(len(analyzer_output[1])):
        print i+1,') ',analyzer_output[1][i]
        if i+1 > 10: break
      print "_____________________________________________________________\n"
      print "Rocchio_V1 with Naive Bayes info deems your activity: ",self.analyzer.danger_r1
      print "Rocchio_V2 with a database info deems your activity:  ",self.analyzer.danger_r2
      self.statusBar().showMessage('Ready for Action!')
    else:
      self.statusBar().showMessage('User entered empty string. Please enter something better!')


