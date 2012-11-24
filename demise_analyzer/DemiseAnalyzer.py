#!/usr/bin/env python
#                                   #
#                                   #
#   CSCE 470 Final Project          #
#   Deadventure Time                #
#   Created by:                     #
#       Juan Burgos                 #
#       Maximilian Leutermann       #
#                                   #
#                                   #

from __future__ import division

import utils, operator, re, itertools, math, random, time, nltk, string

import nltk.classify.util
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import movie_reviews # For semantic analysis to be performed for NaiveBayes
from nltk.stem.wordnet import WordNetLemmatizer

from collections import defaultdict, Counter

from apiclient.discovery import build

class DemiseAnalyzer(object):
    def __init__(self):
        lmtzr = WordNetLemmatizer()
        # set the danger level to neutral
        self.danger = "neutral"
        # import negative words
        self.negative_words = []
        negative_words_import = set(line.strip() for line in open('./data/negative_words.txt'))
        for word in negative_words_import:
            self.negative_words.append(lmtzr.lemmatize(word,'v'))
        self.negative_words = set(self.negative_words)
        del negative_words_import
        # import positive words
        self.positive_words = []
        positive_words_import = set(line.strip() for line in open('./data/positive_words.txt'))
        for word in positive_words_import:
            self.positive_words.append(lmtzr.lemmatize(word,'v'))
        self.positive_words = set(self.positive_words)
        del positive_words_import
        # set up structure for classifying web search results
        self.weblinks = []
        self.trainNaiveBayes()

    def trainNaiveBayes(self):
        negids = movie_reviews.fileids('neg')
        posids = movie_reviews.fileids('pos')
        negfeats = [(utils.word_feats(movie_reviews.words(fileids=[f])),'neg') for f in negids]
        posfeats = [(utils.word_feats(movie_reviews.words(fileids=[f])),'pos') for f in posids]
        trainfeats = negfeats[:] + posfeats[:]
        self.classifier = NaiveBayesClassifier.train(trainfeats)

    def pre_fabricate(self, results):
        # this is a temoprary method until we get the correct JSONs from the Google search
        snippets = list()
        for result in results:
            for item in result["items"]:
                snippets.append(item["snippet"])
        return snippets

    def onlineSearch(self,num_bad_words,num_google_pages,activity_query):
        print "User activity_query = %s" % (activity_query)
        print "--------------------------------------------------------"
        print "Building service client..."
        service = build("customsearch","v1",developerKey="AIzaSyBxbY4NLqH7WWlq1Hgzcqsq29wz8d730o8")
        print "complete!"
        qresults = []
        num_google_pages = min(num_google_pages,10)
        add_words = [''] + random.sample(self.negative_words,num_bad_words)
        print "# of randomly sampled negative terms: %d" % (num_bad_words)
        print "Negative term samples:",add_words
        print "--------------------------------------------------------"
        print "Commencing custom search queries..."
        for i in xrange(num_google_pages):
          i+=1
          for j in xrange(len(add_words)):
            qresults.append(service.cse().list( q=activity_query,
                                                cx='006235170055801286300:e4l76z05biw',
                                                start=i,
                                                num=10,
                                                hq=add_words[j]).execute())
        results = []
        for page in qresults:
          for item in page['items']:
            snip = item['snippet'].encode('utf-8')
            link = item['link'].encode('utf-8')
            self.weblinks.append(link)
            results.append(snip)
        print "Completed all queries, displaying snippet results below:"
        print "--------------------------------------------------------"
        for i in xrange(len(results)):
          print i+1,')',results[i]
        print "--------------------------------------------------------"
        return results

    def OneDimRocchio(self):
        poscount, negcount = 0, 0
        for url in self.weblinks:
          pass
          # for each url, get all sentences using the web scraper.
          # then find the sentences that contain terms in our positive and negative term lists.
          # pull all the verbs out of these sentences for later use in determining cause of demise.
          # run classifier on each of these sentences and accumulate results in poscount and negcount respectively.

    def createResults(self, snippets):
        # create one long string from a list of strings appending a period to the end of each string
        str = string.join(snippets,". ")
        # split string into sentences
        sentences = nltk.sent_tokenize(str)
        # create a list of all tokens in each sentence
        sentences = [list(set(nltk.word_tokenize(sent))) for sent in sentences]
        # tag parts of speech for each word
        sentences = [nltk.pos_tag(sent) for sent in sentences]
        # pull out verbs
        grammar = r"""
                  CHUNK:
                  {<V.*>}
                  }<VBZ>{
                  """
        cp = nltk.RegexpParser(grammar)
        verbs = []
        lmtzr = WordNetLemmatizer()
        for sentence in sentences:
            tree = cp.parse(sentence)
            for subtree in tree.subtrees():
                if subtree.node == 'CHUNK':
                    # map verbs to word-net of closest root word
                    verbs.append(lmtzr.lemmatize(subtree[0][0],'v'))

        # return results in order of liklihood
        return [pair[0] for pair in sorted( self.__sentimentDetermination__(verbs).items(),
                                            key=lambda item: item[1],
                                            reverse = True)]

    def __sentimentDetermination__(self, verbs):
        # count the number of times each verb occurs
        countedVerbs = dict(Counter(verbs))

        positiveVerbs = 0
        negativeVerbs = 0

        # find any words that are in the negative_words list
        keepNegativeVerbs = set(verbs).intersection(self.negative_words)

        # find any words that are in the positive_words list
        keepPositiveVerbs = set(verbs).intersection(self.positive_words)

        # delete any verbs from the counter that are not in the negative_words list
        for word in countedVerbs.keys():
            if word in keepPositiveVerbs:
                positiveVerbs += countedVerbs[word]

        # delete any verbs from the counter that are not in the negative_words list
        for word in countedVerbs.keys():
            if word not in keepNegativeVerbs:
                del countedVerbs[word]

        negativeVerbs = sum(countedVerbs.values())

        # set danger level based on TF:
        #   difference of 0 - 10 neutral
        #   difference of 11 - 25 dangerous/safe
        #   difference of 26< very dangerous/safe

        danger = positiveVerbs - negativeVerbs

        if danger > 25:
            self.danger = "very safe"
        elif danger > 10:
            self.danger = "safe"
        elif danger > -11:
            self.danger = "neutral"
        elif danger > -26:
            self.danger = "dangerous"
        else:
            self.danger = "very dangerous"

        return countedVerbs

def main(): # For testing purposes
    '''
    users_import = set(line.strip() for line in open('mars_tweets_intermediate.json'))
    cluster = Cluster()
    cluster.vectorize(iter(users_import))
    '''
    analyzer = DemiseAnalyzer()
    results = utils.read_results()
    print "\n_____________________________________________________________\nWhen doing this activity you are most likely to: "
    count = 1
    for item in analyzer.createResults(analyzer.pre_fabricate(results)):
        print count,item
        count += 1
    print "_____________________________________________________________\n"

if __name__=="__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    print 'done with constructing results after %.3f seconds'%(end_time-start_time)
