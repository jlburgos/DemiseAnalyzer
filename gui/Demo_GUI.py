#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
sys.path.append("./demise_analyzer")

from DemiseAnalyzer import DemiseAnalyzer
from PyQt4 import QtGui


class DemiseAnalyzerDemo(QtGui.QWidget):
  def __init__(self):
    super(DemiseAnalyzerDemo, self).__init__()
    self.initUI()

  def initUI(self):
    # Configure DemiseAnalyzer
    self.analyzer = DemiseAnalyzer()

    # Button to control Dialog Box
    self.btn = QtGui.QPushButton('Provide Activity', self)
    self.btn.move(20, 20)
    self.btn.setToolTip('Click this button to provide an activity query.')
    self.btn.clicked.connect(self.showDialog)

    # Configure Window
    self.setGeometry(300, 300, 400, 250)
    self.setWindowTitle('Demise Analyzer Demo Application')
    self.setWindowIcon(QtGui.QIcon('./img/trollface.png'))
    self.show()

  def showDialog(self):
    text, ok = QtGui.QInputDialog.getText(self, 'Provide Activity', 'User Activity:')
    self.show()
    if ok and text != "":
      print "Analyzing Activity Query: ",text
      google_results = self.analyzer.onlineSearch(num_bad_words=1,num_google_pages=1,activity_query=text)
      analyzer_output = self.analyzer.createResults(google_results)

      print "\n_____________________________________________________________\n,"
      print "When doing this activity you are most likely to: "
      count = 1
      for item in analyzer_output:
        print count,') ',item
        count += 1
      print "_____________________________________________________________\n"
      print "Your activity has been deemed:",self.analyzer.danger
      print "Finished with analysis!"


