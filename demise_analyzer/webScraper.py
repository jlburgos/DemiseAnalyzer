#!/usr/bin/env python

import nltk
import urllib
from urllib import urlopen

def scrapWebPage(url):
  try:
    html = urlopen(url).read()
    html = nltk.clean_html(html)
    html = nltk.sent_tokenize(html)
    for i in xrange(len(html)):
      for sentence in html:
        sentence = html[i]
        sentence = sentence.replace('\n ',' ').replace(' \n',' ').replace('\n',' ')
        sentence = sentence.replace('\t ',' ').replace(' \t',' ').replace('\t',' ')
        html[i] = sentence
    return html
  except IOError:
    print 'ERROR: URL =',url,'has blocked connection, will return [\'\'] from this src.'
    return ['']

def main(): # Test method
  url = "http://www.sciencedaily.com/releases/2012/11/121125193051.htm"
  print "url =",url
  html = scrapWebPage(url)
  print "html="
  for sentence in html:
    print "---------------------------------------------------------------------------------------------------------"
    print sentence

if __name__=="__main__":
  pass
  #main()
