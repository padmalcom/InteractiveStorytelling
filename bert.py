from __future__ import absolute_import, division, print_function, unicode_literals

from transformers import pipeline
import nltk
from nltk.stem import WordNetLemmatizer 

class Bert:
    def __init__(self):
        self.nlp = pipeline('fill-mask')
        self.lemmatizer = WordNetLemmatizer() 
    
    def getBestPredicateAndProbability(self, subj, obj, lemmatize=True, random=True):
        res = self.nlp(subj + " <mask> " + obj + ".")
        for r in res:
            sentence = r['sequence'].replace("<s>", "").replace("</s>", "")
            words = nltk.word_tokenize(sentence)
            results = []
            for i in range(len(words)):
                if words[i] == subj and i<len(words):
                    verb = words[i+1]
                    if lemmatize == True:
                        print("Lemmatizing " + verb + "...")
                        verb = self.lemmatizer.lemmatize(verb, pos='v')
                        print("to " + verb)
                    if not random:
                        return verb, r['score']
                    else:
                        results.append(tuple(verb, verb, r['score']))

        if len(results) > 0:
            if random:
                choice = random.choice(results)
                return choice[0], choice[1]
            else:
                return results[0][0], results[0][1]
        else:
            return "", 0.0

    def combineTo(self, item1, item2):
        res = self.nlp("He combined the " + item1 + " and the " + item2 + " to a <mask>.")
        for r in res:
            sentence = r['sequence'].replace("<s>", "").replace("</s>", "")
            words = nltk.word_tokenize(sentence)
            if len(words) > 1:
                return words[-2], r['score']
        return "", 0.0