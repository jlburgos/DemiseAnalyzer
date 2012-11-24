#!/usr/bin/env python

import nltk
import urllib
from urllib import urlopen

def scrapWebPage(url):
  html = urlopen(url).read()
  html = nltk.clean_html(html)
  html = nltk.sent_tokenize(html)
  for i in xrange(len(html)):
  for sentence in html:
    sentence = html[i]
    sentence = sentence.replace('\n ',' ').replace(' \n',' ').replace('\n',' ')
    html[i] = sentence
  return html
