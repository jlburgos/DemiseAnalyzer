#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
ZetCode PyQt4 tutorial 

This example shows text which 
is entered in a QtGui.QLineEdit
in a QtGui.QLabel widget.
 
author: Jan Bodnar
website: zetcode.com 
last edited: August 2011
"""

import sys
from PyQt4 import QtGui, QtCore

class Example(QtGui.QWidget):
    
    def __init__(self):
        super(Example, self).__init__()
        
        self.initUI()
        
    def initUI(self):      
        self.mine = QtGui.QLabel(self)
        
        self.lbl = QtGui.QLabel(self)
        qle = QtGui.QLineEdit(self)
        
        qle.move(60, 100)
        self.lbl.move(60, 40)

        qle.textChanged[str].connect(self.onChanged)
        
        self.setGeometry(300, 300, 700, 700)
        self.setWindowTitle('QtGui.QLineEdit')
        
        self.total = QtGui.QTextEdit(self)
        self.total.setText("lolololo\nasdfasdfasdf")
        self.total.move(100,200)
        self.show()
        
    def onChanged(self, text):
        
        self.lbl.setText(text)
        self.lbl.adjustSize()
        
        self.mine.setText("LOLLOL");
        self.mine.adjustSize()
        self.mine.move(30,10)
        self.show()
        
                
        
        
def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
