from nltk.tokenize import RegexpTokenizer
from stop_words import get_stop_words
from nltk.stem.porter import PorterStemmer
from gensim import corpora, models
from gensim.models.coherencemodel import CoherenceModel
import gensim
from nltk import pos_tag
import nltk

# sources:
# https://rstudio-pubs-static.s3.amazonaws.com/79360_850b2a69980c4488b1db95987a24867a.html
# https://radimrehurek.com/gensim/models/coherencemodel.html
class Coherence:
    def __init__(self):
        print("Initializing...")
        try:
            nltk.data.find('taggers\averaged_perceptron_tagger')
        except LookupError:
            nltk.download('averaged_perceptron_tagger')

        self.tokenizer = RegexpTokenizer(r'\w+')
        self.en_stop = get_stop_words('en')
        self.p_stemmer = PorterStemmer()

    def calculateCoherence(self, paragraphs, nouns_only=True):
        texts = []
        is_noun = lambda pos: pos[:2] == 'NN'
        for i in paragraphs:
    
            # clean and tokenize document string
            raw = i.lower()
            tokens = self.tokenizer.tokenize(raw)

            # remove stop words from tokens
            stopped_tokens = [i for i in tokens if not i in self.en_stop]

            # nouns only
            if (nouns_only):
                stopped_tokens = [word for (word, pos) in pos_tag(stopped_tokens) if is_noun(pos)]

            # stem tokens
            stemmed_tokens = [self.p_stemmer.stem(i) for i in stopped_tokens]
            
            # add tokens to list
            texts.append(stemmed_tokens)
        dictionary = corpora.Dictionary(texts)
        corpus = [dictionary.doc2bow(text) for text in texts]
        ldamodel = gensim.models.ldamodel.LdaModel(corpus, num_topics=3, id2word = dictionary, passes=20)
        #print(ldamodel.show_topics())
        topics = []
        for idx, topic in ldamodel.show_topics(formatted=False, num_words= 30):
            #print('Topic: {} \nWords: {}'.format(idx, [w[0] for w in topic]))
            topics.append([w[0] for w in topic])
        cm = CoherenceModel(model=ldamodel, corpus=corpus, coherence='u_mass')
        return cm.get_coherence(), topics