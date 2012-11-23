#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
ZetCode PyQt4 tutorial 

This example shows
how to use QtGui.QSplitter widget.
 
author: Jan Bodnar
website: zetcode.com 

modified by: Juan Burgos
last edited: November 2012
"""

import sys
from PyQt4 import QtGui, QtCore

#################################################################################

class DemiseAnalyzerApp(QtGui.QWidget):
  def __init__(self):
    super(DemiseAnalyzerApp, self).__init__()
    self.initUI()
    
  def initUI(self):   
    # Button Controls
    QtGui.QToolTip.setFont(QtGui.QFont('SansSerif', 10))

    self.setToolTip('This is a <b>QWidget</b> widget')

    btn = QtGui.QPushButton('Button', self)
    btn.setToolTip('This is a <b>QPushButton</b> widget')
    btn.resize(btn.sizeHint())
    btn.move(50, 50)
    
    # Window Configuration
    self.setGeometry(300, 300, 300, 200)
    self.setWindowTitle('Demise Analyzer Demo')
    self.setWindowIcon(QtGui.QIcon('trollface.png'))
    self.show()
    
  def onChanged(self, text):
    self.lbl.setText(text)
    self.lbl.adjustSize()        
        
#################################################################################

def main():
  app = QtGui.QApplication(sys.argv)
  ex = DemiseAnalyzerApp()
  sys.exit(app.exec_())

if __name__ == '__main__':
  main()    
