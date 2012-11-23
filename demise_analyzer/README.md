DemiseAnalyzer
==============

CS 470 Final Project
-- Demise Analyzer --

----------------------------------------------------------------------
### Quick Introduction

This project is designed to read in an activity query such as "swimming", "eating", "scuba diving", etc. and analyzes your chances for survival/death and provides you with a list of possible negative outcomes to your activity.

At the moment, the code that is available has the functionality that queries google search results for information disabled. At this time we are still building our web crawler so the program currently parses a .json file that we've included in place of google. Also included are two text files containing a list of "positive" and "negative" terms that our system uses to identify potential outcomes of your activity.

At the moment we have a simplified 1D Rocchio classifier that classifies the user's activity as either "safe" or "unsafe", providing certain degrees for each.

----------------------------------------------------------------------
### System Requirements

In order to run our application, you need to have the natural language toolkit (NLTK) fully installed into your system, along with a json reading module.

To run our test file type the following into the terminal:
`python DemiseAnalyzerTest.py`

