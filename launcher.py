#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
sys.path.append("./gui")

from Demo_GUI import DemiseAnalyzerDemo
from PyQt4 import QtGui

def main():
  app = QtGui.QApplication(sys.argv)
  ex = DemiseAnalyzerDemo()
  sys.exit(app.exec_())


if __name__ == '__main__':
  main()
