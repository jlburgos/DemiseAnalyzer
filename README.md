DemiseAnalyzer
==============

CS 470 Final Project
-- Demise Analyzer --

----------------------------------------------------------------------
### Quick Introduction

This project is designed to read in an activity query such as "swimming", "eating", "scuba diving", etc. and analyzes your chances for survival/death and provides you with a list of possible negative outcomes to your activity.

Our program begins by taking in the user query and searching google with it as the base. We then randomly sample a negative term from a list of negative search terms as part of an OR-query. Our scraper then visits each webpage that is identified and scrapes all of the text. Using the text and a simplified 1D Rocchio classifier, we classify the user's activity as either "safe" or "dangerous", while providing certain degrees of severity for each for each.  Once the activity's safety rating has been computed by our Rocchio classifer, we use multi-threaded calls to nltk to tokenize and provide "part-of-speech" tagging of every word in every sentence that we scrape from all of the webpages. Using these tagged tokens and verb/noun grammars for our regex parsers (provided by nltk) we attempt to identify verb/noun pairings that may provide cause and effect solutions to your query. This means that along with identifying whether your activity is safe or not safe, we can also attempt to predict what might occur during your activity.

----------------------------------------------------------------------
### System Requirements

System Requirements:
2 Physical Cores, since we recently introduced multi-threading;
Python 2.7+;
NLTK Completely installed (include movie review corpus);
PyQT4;
and Google's Custom Search API (apiclient.discovery).

To run our test file type the following into the terminal from the project directory:
`python launcher.py`

A simple gui will appear with a button and popup window. When running the program on a given query activity, please note that it may take as much as 130 seconds to finish running.
