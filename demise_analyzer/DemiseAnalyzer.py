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
import operator, re, itertools, math, random, nltk, string
from collections import defaultdict, Counter
from web_scraper import scrap_web_page
from features import word_feats

import nltk.classify.util
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import movie_reviews
from nltk.stem.wordnet import WordNetLemmatizer

from sklearn import linear_model

from apiclient.discovery import build

class DemiseAnalyzer(object):
    def __init__(self):
        # set the danger level to neutral
        self.danger_r1 = "neutral" # Rocchio with Naive Bayes
        self.danger_r2 = "neutral" # Rocchio with pos/neg word lists

        # instantiate word net
        self.lmtzr = WordNetLemmatizer()

        # import negative words
        self.negative_words = []
        negative_words_import = set(line.strip() for line in open('./data/negative_words.txt'))
        for word in negative_words_import:
            self.negative_words.append(self.lmtzr.lemmatize(word,'v'))
        self.negative_words = set(self.negative_words)
        del negative_words_import

        # import positive words
        self.positive_words = []
        positive_words_import = set(line.strip() for line in open('./data/positive_words.txt'))
        for word in positive_words_import:
            self.positive_words.append(self.lmtzr.lemmatize(word,'v'))
        self.positive_words = set(self.positive_words)
        del positive_words_import

        # set up structure for classifying web search results
        self.web_links = []
        self.train_classifiers()

    def train_classifiers(self):
        negids = movie_reviews.fileids('neg')
        posids = movie_reviews.fileids('pos')
        negfeats = [(word_feats(movie_reviews.words(fileids=[f])),'neg') for f in negids]
        posfeats = [(word_feats(movie_reviews.words(fileids=[f])),'pos') for f in posids]
        trainfeats = negfeats + posfeats

        # train naive bayes
        self.classifier = NaiveBayesClassifier.train(trainfeats)

        # train linear regression model
        #self.regr = linear_model.LinearRegression()
        #self.regr.fit(jk

    #deprecated
    def preprocess_information(self, results):
        # this is a temporary method until we get the correct JSONs from the Google search
        snippets = list()
        for result in results:
            for item in result["items"]:
                snippets.append(item["snippet"])
        return snippets

    def min_proximity_query(self,verb_set,noun_set,sentence):
        pack = ('','',len(sentence)) # (verb,noun,min_dist)
        for verb in verb_set:
          for noun in noun_set:
            dist = abs(sentence.index(verb) - sentence.index(noun))
            if dist < pack[2] and self.classifier.classify(word_feats(verb+' '+noun))=='neg':
              pack = (verb,noun,dist)
        return pack[0].lower(),pack[1].lower()

    def online_search(self,num_bad_words,num_google_pages,activity_query):
        print "User activity_query = %s" % (activity_query)
        print "--------------------------------------------------------"
        print "Building service client..."
        service = build("customsearch","v1",developerKey="AIzaSyBxbY4NLqH7WWlq1Hgzcqsq29wz8d730o8")
        print "complete!"
        qresults = []
        num_google_pages = min(num_google_pages,10)
        add_words = [''] + random.sample(['die','death','kill','accident','injury','hurt'],num_bad_words)
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

        # Scrape all the web pages of interest
        html_sentences = []
        for url in self.web_links:
          html_sentences += scrap_web_page(url)
        print "Processing %d sentences." % len(html_sentences)

        # Count the number of pos/neg sentences and record all negative sentences
        neg_sentences = []
        poscount, negcount = 0, 0
        for i in xrange(len(html_sentences)):
          sent = html_sentences[i]
          sentiment = self.classifier.classify(word_feats(sent))
          if sentiment == 'pos':
            poscount += 1
          else:
            negcount += 1
            neg_sentences.append(sent)

        # Compute sentiment with Rocchio as the balancer
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

        # Record danger level as interpreted by Rocchio using Naive Bayes as a subroutine
        self.danger_r1 = level + ' ' + sentiment

        # Randomly sample from the remaining negative sentences
        samp = min(max_num_sentences,len(neg_sentences))
        html_sentences = random.sample(neg_sentences,samp)
        return self.create_results(html_sentences)

    def create_results(self, orig_sentences):
        print 'Running nltk subroutines in create_results()'

        # create a list of all tokens in each sentence
        sentences = [nltk.word_tokenize(sent) for sent in orig_sentences]
        # tag parts of speech for each word
        sentences = [nltk.pos_tag(sent) for sent in sentences]

        # Verb Extraction Grammar
        grammar = r"""
                  CHUNK0: {<V.*>}
                          }<VBZ>{
                  CHUNK1: {<VBD>|<VBN>}
                  CHUNK2: {<VBZ><RB>}
                  CHUNK3: {<VBN><IN><DT><NN>}
                  """
        # Verb Regex Parser (Finds effects)
        cp_effect = nltk.RegexpParser(grammar)

        # Noun Extraction Grammar
        grammar2 = r'CHUNK: {<NN|NP>}'
        # Noun Regex Parser (Finds causes)
        cp_cause = nltk.RegexpParser(grammar2)

        """
        all_verbs = []
        neg_sentences = []

        for i in xrange(len(sentences)):
          original = orig_sentences[i]
          sentence = sentences[i]

          # Collect all verbs
          tree = cp_effect.parse(sentence)
          for subtree in tree.subtrees():
            if subtree.node in ['CHUNK0','CHUNK1','CHUNK2','CHUNK3']:
              term = self.lmtzr.lemmatize(subtree[0][0],'v')
              all_verbs.append(term)

        # Record overall sentiment for Rocchio w/ database through analysis of all the verbs
        self.determine_sentiment(all_verbs,True)

        # Find the part-of-speach for each of these verbs
        mod_neg_sentences = [list(set(nltk.word_tokenize(sent))) for sent in neg_sentences]
        mod_neg_sentences = [nltk.pos_tag(sent) for sent in mod_neg_sentences]
        """

        verbs = []
        nouns = []

        # Gather only the most negative sentences and process them with nltk
        #
        # The reason behind this is that we want to have two lists produced:
        #
        # List verbs[] and List nouns[], both of which are lists of lists where
        # each sublist corresponds to an individual 'negative sentence'.

        for sent in mod_neg_sentences:
          # Collect Negative Verbs
          some_verbs = []
          tree1 = cp_effect.parse(sent)
          for subtree in tree1.subtrees():
            if subtree.node in ['CHUNK0','CHUNK1','CHUNK2','CHUNK3']:
              term = self.lmtzr.lemmatize(subtree[0][0],'v')
              if self.classifier.classify(word_feats(term)) == 'neg':
                some_verbs.append(term)
          verbs.append(some_verbs)
          # Collect Nouns
          some_nouns = []
          tree2 = cp_cause.parse(sent)
          for subtree in tree2.subtrees():
            if subtree.node in ['CHUNK']:
              term = self.lmtzr.lemmatize(subtree[0][0],'n')
              some_nouns.append(term)
          nouns.append(some_nouns)

        # Find the most negative verb/noun pairs and produce 'good' phrases
        phrases = []
        for i in xrange(len(neg_verbs)):
          verb_set = neg_verbs[i]
          noun_set = nouns[i]
          ####################################################################
          print 'Need to modify min_prox query to take in tokenized sentence with pos tags'
          exit()
          ####################################################################
          if len(verb_set)==0 or len(noun_set)==0:
            continue
          v,n = self.min_proximity_query(verb_set,noun_set,orig_sentences[i])
          if len(v)>2 and len(n)>2:
            ss = v + ' ' + n
            phrases.append(v+' '+n)

        #phrases = list(set(phrases))
        print "len phrases = ",len(phrases)
        print "len nouns = ",len(nouns)
        print "len verbs = ",len(verbs)

        # TODO :: For now we are returning 15 randomly sampled results, fix this!
        return random.sample(phrases,15)

        ##############################################3
        print "SHOULD NEVER SEE THIS LINE!!!"
        exit()
        ##############################################3

        #nouns = [noun for noun in nouns if self.classifier.classify(word_feats(noun))=='neg']
        #verbs = [pair[0] for pair in sorted(self.determine_sentiment(verbs,True).items(), key=lambda item: item[1], reverse=True)]
        #return verbs[:15]

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

        # For Rocchio V2
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

