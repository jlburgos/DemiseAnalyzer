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
from collections import defaultdict, Counter
from webScraper import scrapWebPage

import nltk.classify.util
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import movie_reviews
from nltk.stem.wordnet import WordNetLemmatizer

from apiclient.discovery import build

class DemiseAnalyzer(object):
    def __init__(self):
        # set the danger level to neutral
        self.danger_r1 = "neutral" # Rocchio with Naive Bayes
        self.danger_r2 = "neutral" # Rocchio with pos/neg word lists

        # instantiate word net
        lmtzr = WordNetLemmatizer()

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
        self.web_links = []
        self.train_naive_bayes()

    def train_naive_bayes(self):
        negids = movie_reviews.fileids('neg')
        posids = movie_reviews.fileids('pos')
        negfeats = [(utils.word_feats(movie_reviews.words(fileids=[f])),'neg') for f in negids]
        posfeats = [(utils.word_feats(movie_reviews.words(fileids=[f])),'pos') for f in posids]
        trainfeats = negfeats[:] + posfeats[:]
        self.classifier = NaiveBayesClassifier.train(trainfeats)

    def preprocess_information(self, results):
        # this is a temoprary method until we get the correct JSONs from the Google search
        snippets = list()
        for result in results:
            for item in result["items"]:
                snippets.append(item["snippet"])
        return snippets

    def online_search(self,num_bad_words,num_google_pages,activity_query):
        print "User activity_query = %s" % (activity_query)
        print "--------------------------------------------------------"
        print "Building service client..."
        service = build("customsearch","v1",developerKey="AIzaSyBxbY4NLqH7WWlq1Hgzcqsq29wz8d730o8")
        print "complete!"
        qresults = []
        num_google_pages = min(num_google_pages,10)
        add_words = ['death']
        #add_words = ['death'] + random.sample(self.negative_words,num_bad_words)
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
        # Clear current web_links
        self.web_links = []
        for page in qresults:
          for item in page['items']:
            snip = item['snippet'].encode('utf-8')
            link = item['link'].encode('utf-8')
            self.web_links.append(link)
            results.append(snip)
        print "Completed all queries, displaying snippet results below:"
        print "--------------------------------------------------------"
        for i in xrange(len(results)):
          print i+1,')',results[i]
        print "--------------------------------------------------------"
        return results

    def rocchio(self,max_num_sentences):
        print 'Running rocchio()'
        poscount, negcount = 0, 0
        html_sentences = []
        for url in self.web_links:
          html_sentences += scrapWebPage(url)
        html_sentences = random.sample(html_sentences,min(max_num_sentences,len(html_sentences)))
        print "Processing %d sentences." % len(html_sentences)

        for i in xrange(len(html_sentences)):
          sent = html_sentences[i]
          sentiment = self.classifier.classify(utils.word_feats(sent))
          if sentiment == 'pos':
            poscount += 1
          else:
            negcount += 1

        sentiment = 'neutral'
        if poscount > negcount:
          sentiment = 'safe'
        elif poscount < negcount:
          sentiment = 'dangerous'
        level = 'mildly'
        if poscount >= 1.25*negcount or negcount >= 1.25*negcount:
          level = 'relatively'
        elif poscount >= 1.5*negcount or negcount >= 1.5*poscount:
          level = 'very'

        self.danger_r1 = level + ' ' + sentiment

        l1 = self.create_results(html_sentences)
        return l1

    def create_results(self, orig_sentences):
        print 'Running nltk subroutines in create_results()'
        # create one long string from a list of strings appending a period to the end of each string
        #sentences = string.join(snippets,". ")
        # remove punctuation marks (comma,period,etc...)
        #for c in string.punctuation:
        #  sentences = sentences.replace(c,"")
        # split string into sentences
        #sentences = nltk.sent_tokenize(sentences)
        # create a list of all tokens in each sentence
        sentences = [list(set(nltk.word_tokenize(sent))) for sent in orig_sentences]
        # tag parts of speech for each word
        sentences = [nltk.pos_tag(sent) for sent in sentences]
        # pull out verbs
        #grammar = r"""
        #          CHUNK:
        #            {<V.*>}
        #            }<VBZ>{
        #          """
        grammar = r"""
                  CHUNK0: {<V.*>}
                          }<VBZ>{
                  CHUNK1: {<VBD>|<VBN>}
                  CHUNK2: {<VBZ><RB>}
                  CHUNK3: {<VBN><IN><DT><NN>}
                  """
        cp_effect = nltk.RegexpParser(grammar)
        all_verbs = []
        neg_sentences = []
        lmtzr = WordNetLemmatizer()

        for i in xrange(len(sentences)):
          original = orig_sentences[i]
          sentence = sentences[i]
          if self.classifier.classify(utils.word_feats(original)) == 'neg':
            if not set(self.negative_words).isdisjoint(original.split(' ')):
              neg_sentences.append((i,original))
          tree = cp_effect.parse(sentence)
          for subtree in tree.subtrees():
            # Collect meaningful verbs
            if subtree.node in ['CHUNK0','CHUNK1','CHUNK2','CHUNK3']:
              term = lmtzr.lemmatize(subtree[0][0],'v')
              all_verbs.append(term)

        all_verbs = [pair[0] for pair in sorted(self.determine_sentiment(all_verbs,True).items(), key=lambda item: item[1], reverse=True)]
        grammar2 = r'CHUNK: {<NN|NP>}'
        cp_cause = nltk.RegexpParser(grammar2)
        nouns = []
        verbs = []

        for sent in neg_sentences:
          # Verbs
          tree = cp_effect.parse(sentence)
          for subtree in tree.subtrees():
            if subtree.node in ['CHUNK0','CHUNK1','CHUNK2','CHUNK3']:
              term = lmtzr.lemmatize(subtree[0],'v')
              some_verbs.append(term)
          verbs.append(some_verbs)

        f = open('information.txt','w')
        for sent in verbs:
          f.write('negative verbs =',sent,'\n\n')
        f.close()
        exit()

        """
          # Nouns
          tree = cp_cause.parse(sent)
          some_nouns = []
          for subtree in tree.subtrees():
            if subtree.node == 'CHUNK':
              some_nouns.append(subtree[0][0])
          nouns.append(some_nouns)
        """

        """
        f = open('information.txt','w')
        for sent in neg_sentences:
          f.write('negative sentence = %s\n' % sent[1])
        f.close()
        """


        """
        nouns = list(set(nouns))
        pairings = []
        for verb in verbs:
          pairing = (verb[1],[])
          for noun in nouns:
            if verb[0] == noun[0]:
              pairing[1].append(noun[1])
              break
          ss = ' '.join(pairing[1])

          pairings.append(pairing)

        f = open('information.txt','w')
        f.write('\n=====================================================\n')
        f.write('pairings :: %d\n' % len(pairings))
        count = 0
        for i in xrange(len(pairings)):
          for j in xrange(len(pairings[i][1])):
            elem = pairings[i][1][j]
            f.write('%s   ' % elem)
          f.write('\n----------------------------------------------------\n')
        f.write('\n=====================================================\n')
        f.write('nouns :: %d\n' % len(nouns))
        count = 0
        for i in xrange(len(nouns)):
          elem = nouns[i]
          count += 1;
          if count < 9:
            f.write('%s   ' % elem[1])
          else:
            count = 0
            f.write('\n%s   ' % elem[1])
        f.write('\n=====================================================\n')
        f.write('verbs :: %d\n' % len(verbs))
        count = 0
        for i in xrange(len(verbs)):
          elem = verbs[i]
          count += 1
          if count < 9:
            f.write('%s   ' % elem[1])
          else:
            count = 0
            f.write('\n%s   ' % elem[1])
        f.write('\n=====================================================\n')
        """
        exit()
        nouns = [noun for noun in nouns if self.classifier.classify(utils.word_feats(noun))=='neg']
        verbs = [pair[0] for pair in sorted(self.determine_sentiment(verbs,True).items(), key=lambda item: item[1], reverse=True)]
        return [nouns[:15],verbs[:15]]

    def determine_sentiment(self, verbs, record_danger):
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
        danger = positiveVerbs - negativeVerbs

        if record_danger:
          if danger > 0:
            if positiveVerbs > 1.25*negativeVerbs:
              self.danger_r2 = "very safe"
            else:
              self.danger_r2 = "safe"
          elif danger == 0:
            self.danger_r2 = "neutral"
          elif danger < 0:
            if negativeVerbs > 1.25*positiveVerbs:
              self.danger_r2 = "dangerous"
            else:
              self.danger_r2 = "very dangerous"

        return countedVerbs

#####################################################################################

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
    for item in analyzer.create_results(analyzer.preprocess_information(results)):
        print count,item
        count += 1
    print "_____________________________________________________________\n"

if __name__=="__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    print 'done with constructing results after %.3f seconds'%(end_time-start_time)
