import sys
sys.path.insert(0,'../src/')
import DemiseAnalyzer, utils, unittest
from collections import Counter

TINY_CORPUS = [
    {"items": [{"snippet": "A flower, sometimes known as a bloom or blossom, is the reproductive structure found in flowering plants (plants of the division Magnoliophyta, ...",}]},
    {"items": [{"snippet": "This is a second returned result. The man drowned and died after skydiving",},]},
    {"items": [{"snippet": "This is a third retuned search result. The man fell off the cliff and died",},]},
    {"items": [{"snippet": "This is a fourth returned reslt. A woman named Marie fell out of an airplane, splat on the ground, and died",},]},
    {"items": [{"kind": "customsearch#result","title": "Flower - Wikipedia, the free encyclopedia","htmlTitle": "\u003cb\u003eFlower\u003c/b\u003e - Wikipedia, the free encyclopedia","link": "http://en.wikipedia.org/wiki/Flower","displayLink": "en.wikipedia.org","snippet": "This is a fifth returned search result. The crazy kid drowned and died after falling off of a diving board and hitting his head on the ground","htmlSnippet": "A \u003cb\u003eflower\u003c/b\u003e, sometimes known as a bloom or blossom, is the reproductive structure \u003cbr\u003e  found in flowering plants (plants of the division Magnoliophyta, \u003cb\u003e... \u003c/b\u003e",},]},
    {"items": [{"kind": "customsearch#result","title": "Flower - Wikipedia, the free encyclopedia","htmlTitle": "\u003cb\u003eFlower\u003c/b\u003e - Wikipedia, the free encyclopedia","link": "http://en.wikipedia.org/wiki/Flower","displayLink": "en.wikipedia.org","snippet": "This is a sixth returned reslt. The man hit his head, drowned and died when he fell out of the boat on the river","htmlSnippet": "A \u003cb\u003eflower\u003c/b\u003e, sometimes known as a bloom or blossom, is the reproductive structure \u003cbr\u003e  found in flowering plants (plants of the division Magnoliophyta, \u003cb\u003e... \u003c/b\u003e",},]},
    {"items": [{"snippet": "If someone goes rock climbing they can break their arm and bleed out and ... die",},]},
]

class TestDemiseAnalyzer(unittest.TestCase):
    def test_initialize(self):
        # this will ensure that the user has NLTK installed and that it is culling properly
        d = DemiseAnalyzer.DemiseAnalyzer()
        self.assertEqual(len(d.negative_words),2388)
        self.assertEqual(len(d.positive_words),249)

    def test_create_results(self):
        # this determines if the result generator is working correctly using the tiny corpus from above
        d = DemiseAnalyzer.DemiseAnalyzer()
        results = d.createResults(d.pre_fabricate(TINY_CORPUS))
        # testing what can go wrong
        self.assertEqual(results, ["drown","die","fall"])
        # determining the degree of "dangerousness"
        self.assertEqual(d.danger, "neutral")

if __name__ == '__main__':
    unittest.main()
