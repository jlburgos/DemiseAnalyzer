#!/usr/bin/env python

import nltk
import urllib
from urllib import urlopen

def scrapWebPage():
  url = 'http://www.alternet.org/truth-about-sleeping-pills-big-pharmas-goldmine'
  html = urlopen(url).read()
  raw = nltk.clean_html(html)
  l2 = nltk.sent_tokenize(raw)
  for i in xrange(len(l2)):
  for sentence in l2:
    sentence = l2[i]
    sentence = sentence.replace('\n ',' ').replace(' \n',' ').replace('\n',' ')
    l2[i] = sentence
  return l2
