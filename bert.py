from __future__ import absolute_import, division, print_function, unicode_literals

from transformers import pipeline
import nltk

class Bert:
    def __init__(self):
        self.nlp = pipeline('fill-mask')
    
    def getBestPredicateAndProbability(self, subj, obj):
        res = self.nlp(subj + " <mask> " + obj)
        for r in res:
            sentence = r['sequence'].replace("<s>", "").replace("</s>", "")
            words = nltk.word_tokenize(sentence)
            print(words)
            for i in range(len(words)):
                if words[i] == subj and i<len(words):
                    return words[i+1], r['score']

    def combineTo(self, item1, item2):
        res = self.nlp("He combined the " + item1 + " and the " + item2 + " to a <mask>.")
        for r in res:
            sentence = r['sequence'].replace("<s>", "").replace("</s>", "")
            words = nltk.word_tokenize(sentence)
            print(words)
            if len(words) > 1:
                return words[-2], r['score']
        return "", 0.0