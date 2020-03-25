from __future__ import absolute_import, division, print_function, unicode_literals

from transformers import pipeline
import nltk
from nltk.stem import WordNetLemmatizer
import random

class Bert:
    def __init__(self):
        self.nlp = pipeline('fill-mask')
        self.lemmatizer = WordNetLemmatizer() 
    
    def getBestPredicateAndProbability(self, subj, obj, lemmatize=True, random_choice=True):
        res = self.nlp(subj + " <mask> " + obj + ".")
        for r in res:
            #print(r)
            sentence = r['sequence'].replace("<s>", "").replace("</s>", "")
            words = nltk.word_tokenize(sentence)
            results = []
            for i in range(len(words)):
                if words[i] == subj and i<len(words):
                    verb = words[i+1]
                    if lemmatize == True:
                        #print("Lemmatizing " + verb + "...")
                        verb = self.lemmatizer.lemmatize(verb, pos='v')
                        #print("to " + verb)
                    if not random_choice:
                        return verb, r['score']
                    else:
                        results.append((verb, r['score']))

        if len(results) > 0:
            choice = random.choice(results)
            return choice[0], choice[1]
        else:
            return "", 0.0

    def combineTo(self, item1, item2):
        res = self.nlp("He combined " + item1 + " and " + item2 + " and received a <mask>.")
        print(res)
        for r in res:
            sentence = r['sequence'].replace("<s>", "").replace("</s>", "")
            words = nltk.word_tokenize(sentence)
            if len(words) > 1:
                return words[-2], r['score']
        return "", 0.0