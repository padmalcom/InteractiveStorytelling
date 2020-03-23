from transformers import pipeline

class Sentiment:
    def __init__(self):
        self.nlp = pipeline('sentiment-analysis')

    def sentiment(self, sentence):
        res = self.nlp(sentence)
        if res[0]['label'] == "NEGATIVE":
            return -1
        else:
            return 1