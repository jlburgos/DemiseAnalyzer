import nltk
import urllib
from urllib import urlopen

def scrap_web_page(url):
  try:
    html = urlopen(url).read()
    html = nltk.clean_html(html)
    html = nltk.sent_tokenize(html)
    for i in xrange(len(html)):
      for sentence in html:
        sentence = html[i]
        html[i] = sentence
    return html
  except IOError:
    print 'Warning: ( URL =',url,') has blocked connection, returning [\'\'].'
    return ['']

