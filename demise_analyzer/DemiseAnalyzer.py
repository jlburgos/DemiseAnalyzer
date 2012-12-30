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
import operator
import re
import itertools
import math
import random
import nltk
import string
from collections import defaultdict, Counter
from web_scraper import scrap_web_page
from features import word_feats

import nltk.classify.util
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import movie_reviews
from nltk.stem.wordnet import WordNetLemmatizer

from sklearn import linear_model
from apiclient.discovery import build
from nltk_thread import myThread


class DemiseAnalyzer(object):
    def __init__(self):
        # set the danger level to neutral
        self.danger_r1 = "neutral"  # Rocchio with Naive Bayes
        self.danger_r2 = "neutral"  # Rocchio with pos/neg word lists

        # instantiate word net
        self.lmtzr = WordNetLemmatizer()

        # import negative words
        self.negative_search_terms = ['die', 'death', 'kill',
                                      'accident', 'injury', 'hurt']
        self.negative_words = []
        negative_words_import = set(
            line.strip() for line in open('./data/negative_words.txt'))
        for word in negative_words_import:
            self.negative_words.append(self.lmtzr.lemmatize(word, 'v'))
        self.negative_words = set(self.negative_words)
        del negative_words_import

        # import positive words
        self.positive_words = []
        positive_words_import = set(
            line.strip() for line in open('./data/positive_words.txt'))
        for word in positive_words_import:
            self.positive_words.append(self.lmtzr.lemmatize(word, 'v'))
        self.positive_words = set(self.positive_words)
        del positive_words_import

        # set up structure for classifying web search results
        self.web_links = []
        self.train_classifiers()

    def train_classifiers(self):
        negids = movie_reviews.fileids('neg')
        posids = movie_reviews.fileids('pos')
        negfeats = [(word_feats(
            movie_reviews.words(fileids=[f])), 'neg') for f in negids]
        posfeats = [(word_feats(
            movie_reviews.words(fileids=[f])), 'pos') for f in posids]
        trainfeats = negfeats + posfeats

        # train naive bayes
        self.classifier = NaiveBayesClassifier.train(trainfeats)

        # TODO :: Linear Regression planned to be used for ranking
        # train linear regression model
        # self.regr = linear_model.LinearRegression()

    def min_proximity_query(self, verb_set, noun_set, sentence):
        pack = ('', '', len(sentence) + 1)  # (verb,noun,min_dist)
        for verb in verb_set:
            if verb not in sentence:
                continue
            for noun in noun_set:
                if noun not in sentence:
                    continue
                dist = abs(sentence.index(verb) - sentence.index(noun))
                if dist < pack[2] and self.classifier.classify(word_feats(verb + ' ' + noun)) == 'neg':
                    pack = (verb, noun, dist)
        return pack[0].lower(), pack[1].lower()

    def proximity_semantic_score(self, i, sentences):
        score = 0
        # read the current sentence and the two sentences before and after it
        for sent in sentences:
            for word in sent:
                if self.classifier.classify(word_feats(word)) == 'neg':
                    score += 1
                    for neg in self.negative_search_terms:
                        if neg == word:
                            score += 1000
        return score

    def online_search(self, num_bad_words, num_google_pages, activity_query):
        print "\n\n========================================================"
        print "User activity_query = %s" % (activity_query)
        print "--------------------------------------------------------"
        print "Building service client..."
        service = build("customsearch", "v1", developerKey="AIzaSyBxbY4NLqH7WWlq1Hgzcqsq29wz8d730o8")
        print "complete!"
        qresults = []
        num_google_pages = min(num_google_pages, 10)
        add_words = [''] + random.sample(
            self.negative_search_terms, num_bad_words)  # used in or-query
        print "# of randomly sampled negative terms: %d" % (num_bad_words)
        print "Negative term samples:", add_words
        print "--------------------------------------------------------"
        print "Commencing custom search queries..."
        for i in xrange(num_google_pages):
            i += 1
            for j in xrange(len(add_words)):
                qresults.append(service.cse().list(q=activity_query,
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
        print "--------------------------------------------------------"
        print "Completed all queries, displaying Google snippet results below:"
        for i in xrange(len(results)):
            print i + 1, ')', results[i]
        print "--------------------------------------------------------"
        return results

    def rocchio(self, max_num_sentences):

        # Scrape all the web pages of interest
        print 'Crawling target webpages and grabbing information...'
        html_sentences = []
        for url in self.web_links:
            print 'Grabbing info from url:', url
            html_sentences += scrap_web_page(url)
        print "\nProcessing %d sentences." % len(html_sentences)

        # Count the number of pos/neg sentences and record all negative
        # sentences
        print 'Running Rocchio()'
        neg_sentences = []
        poscount, negcount = 0, 0
        for i in xrange(len(html_sentences)):
            sent = html_sentences[i]
            sentiment = self.classifier.classify(word_feats(sent))
            if sentiment == 'pos':
                poscount += 2.5  # positives are worth 250% that of negatives
            else:
                negcount += 1
                neg_sentences.append(sent)
        poscount = math.ceil(poscount)

        # Compute sentiment with Rocchio as the balancer
        print 'pos_count =', poscount
        print 'neg_count =', negcount
        sentiment = 'neutral'
        level = 'mildly'
        if poscount > negcount:
            sentiment = 'safe'
        elif poscount < negcount:
            sentiment = 'dangerous'
        if poscount >= 2 * negcount or negcount >= 2 * negcount:
            level = 'relatively'
        elif poscount >= 4 * negcount or negcount >= 4 * poscount:
            level = 'very'

        # Record danger level as interpreted by Rocchio using Naive Bayes as a
        # subroutine
        self.danger_r1 = level + ' ' + sentiment

        # Randomly sample from the remaining negative sentences
        samp = min(max_num_sentences, len(neg_sentences))
        html_sentences = random.sample(neg_sentences, samp)
        return self.create_results(html_sentences)

    def create_results(self, orig_sentences):
        print 'Running nltk subroutines in create_results()'

        # create a list of all tokens in each sentence
        sentences = [nltk.word_tokenize(sent) for sent in orig_sentences]
        # record the tokenized sentences separately
        tokenized_sentences = sentences

        # multi-threaded pos_tag assignment
        print 'Running multi-threaded "part-of-speech" tagging of web page results'
        t1 = myThread(1, 3, tokenized_sentences)
        t2 = myThread(2, 3, tokenized_sentences)
        t3 = myThread(3, 3, tokenized_sentences)

        # TODO :: currently hard-coded to 3 threads for now
        threads = []
        t1.start()
        t2.start()
        t3.start()

        threads.append(t1)
        threads.append(t2)
        threads.append(t3)

        # Wait for all threads to be done
        for t in threads:
            t.join()

        # tag parts of speech for each word
        sentences = t1.results + t2.results + t3.results

        print "Constructing Grammars..."
        # Verb Extraction Grammar
        grammar = r"""
                  VERBS: {<V.*>}
                          }<VBZ>{
                  """
        # Verb Regex Parser (Finds effects)
        cp_effect = nltk.RegexpParser(grammar)

        # Noun Extraction Grammar
        grammar2 = r'NOUNS: {<NN|NP>}'
        # Noun Regex Parser (Finds causes)
        cp_cause = nltk.RegexpParser(grammar2)

        verbs = []
        nouns = []

        # Gather only the most negative sentences and process them with nltk
        #
        # The reason behind this is that we want to have two lists produced:
        #
        # List verbs[] and List nouns[], both of which are lists of lists where
        # each sublist corresponds to an individual 'negative sentence'.

        print "Parsing all sentences and collecting verbs and nouns..."
        for sent in sentences:

            # Collect Negative Verbs
            some_verbs = []
            tree1 = cp_effect.parse(sent)
            for subtree in tree1.subtrees():
                if subtree.node in ['VERBS']:
                    term = self.lmtzr.lemmatize(subtree[0][0], 'v')
                    if self.classifier.classify(word_feats(term)) == 'neg':
                        some_verbs.append(term)
            verbs.append(some_verbs)

            # Collect Nouns
            some_nouns = []
            tree2 = cp_cause.parse(sent)
            for subtree in tree2.subtrees():
                if subtree.node in ['NOUNS']:
                    term = self.lmtzr.lemmatize(subtree[0][0], 'n')
                    some_nouns.append(term)
            nouns.append(some_nouns)

        # Find the most negative verb/noun pairs and produce 'good' phrases
        print "Collecting (verb,noun) pairings..."
        phrases = []
        num_sents = len(tokenized_sentences)
        for i in xrange(num_sents):
            verb_set = verbs[i]
            noun_set = nouns[i]
            if len(verb_set) == 0 or len(noun_set) == 0:
                continue
            v, n = self.min_proximity_query(
                verb_set, noun_set, tokenized_sentences[i])
            rating = self.proximity_semantic_score(
                i, orig_sentences[i - 1:i + 1])
            if len(v) > 2 and len(n) > 2:
                ss = v + ' ' + n
                phrases.append((v + ' ' + n, rating, orig_sentences[i]))

        print "len phrases = ", len(phrases)
        print "len nouns = ", len(nouns)
        print "len verbs = ", len(verbs)

        # Returning 10 randomly sampled results, fix this!
        print "Removing duplicates and porting phrases by negativity scores."
        phrases = list(set(phrases))
        phrases = sorted(phrases, key=lambda tup: tup[1], reverse=True)
        print "Returning top 10 phrases."
        return phrases[:10]

    # deprecated
    def preprocess_information(self, results):
        # this is a temporary method until we get the correct JSONs from the
        # Google search
        snippets = list()
        for result in results:
            for item in result["items"]:
                snippets.append(item["snippet"])
        return snippets

    # deprecated
    def determine_sentiment(self, verbs, record_danger):
        # count the number of times each verb occurs
        countedVerbs = dict(Counter(verbs))
        positiveVerbs = 0
        negativeVerbs = 0

        # find any words that are in the negative_words list
        keepNegativeVerbs = set(verbs).intersection(self.negative_words)

        # find any words that are in the positive_words list
        keepPositiveVerbs = set(verbs).intersection(self.positive_words)

        # delete any verbs from the counter that are not in the negative_words
        # list
        for word in countedVerbs.keys():
            if word in keepPositiveVerbs:
                positiveVerbs += countedVerbs[word]

        # delete any verbs from the counter that are not in the negative_words
        # list
        for word in countedVerbs.keys():
            if word not in keepNegativeVerbs:
                del countedVerbs[word]

        negativeVerbs = sum(countedVerbs.values())
        danger = positiveVerbs - negativeVerbs

        # For Rocchio V2
        if record_danger:
            if danger > 0:
                if positiveVerbs > 1.25 * negativeVerbs:
                    self.danger_r2 = "very safe"
                else:
                    self.danger_r2 = "safe"
            elif danger == 0:
                self.danger_r2 = "neutral"
            elif danger < 0:
                if negativeVerbs > 1.25 * positiveVerbs:
                    self.danger_r2 = "dangerous"
                else:
                    self.danger_r2 = "very dangerous"

        return countedVerbs
