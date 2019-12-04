from nltk.tokenize import RegexpTokenizer
from stop_words import get_stop_words
from nltk.stem.porter import PorterStemmer
from gensim import corpora, models
from gensim.models.coherencemodel import CoherenceModel
import gensim

# sources:
# https://rstudio-pubs-static.s3.amazonaws.com/79360_850b2a69980c4488b1db95987a24867a.html
# https://radimrehurek.com/gensim/models/coherencemodel.html
class Coherence:
    def __init__(self):
        print("Initializing...")
        self.tokenizer = RegexpTokenizer(r'\w+')
        self.en_stop = get_stop_words('en')
        self.p_stemmer = PorterStemmer()

    def calculateCoherence(self, paragraphs):
        texts = []
        for i in paragraphs:
    
            # clean and tokenize document string
            raw = i.lower()
            tokens = self.tokenizer.tokenize(raw)

            # remove stop words from tokens
            stopped_tokens = [i for i in tokens if not i in self.en_stop]
            
            # stem tokens
            stemmed_tokens = [self.p_stemmer.stem(i) for i in stopped_tokens]
            
            # add tokens to list
            texts.append(stemmed_tokens)
        dictionary = corpora.Dictionary(texts)
        corpus = [dictionary.doc2bow(text) for text in texts]
        ldamodel = gensim.models.ldamodel.LdaModel(corpus, num_topics=2, id2word = dictionary, passes=20)
        cm = CoherenceModel(model=ldamodel, corpus=corpus, coherence='u_mass')
        return cm.get_coherence()