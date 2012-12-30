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
                sentence = sentence.replace('\t', '')
                sentence = sentence.replace('\n', '')
                sentence = sentence.replace('  ', ' ')
                html[i] = sentence
        return html
    except IOError:
        print 'Returning [\'\'] due to failed connection attempt to url:', url
        return ['']
