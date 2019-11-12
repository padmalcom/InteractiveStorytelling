from collections import Counter, defaultdict

# nlp
import spacy
import en_core_web_lg
import nltk
from nltk import ngrams
from nltk.corpus import reuters
from nltk import bigrams, trigrams
from nltk.corpus import wordnet as wn
from textblob import TextBlob

# custom
from gpt2 import GPT2
from actiontemplates import ActionTemplates
from item import items
from setting import settings

class StoryGenerator():

    def __init__(self):
        self.inventory = []
        self.known_places = []
        self.known_people = []
        self.nlp = spacy.load("en_core_web_lg")
        self.introduction = ""
        self.items_in_paragraph = []
        self.places_in_paragraph = []
        self.people_in_paragraph = []
        self.events_in_paragraph = []
        self.nouns_in_paragraph = []
        self.current_paragraphs = 0 # Tract current paractraph
        self.name = ""
        self.setting = ""
        self.setting_id = 0
        self.text = ""
        self.html = "<html><body>"
        self.HTML_END = "</body></html>"
        self.gpt2 = GPT2(dummy=True)
        self.USE_NOUNS = True
        self.MAX_ACTIONS = 18
        self.actionTemplates = ActionTemplates()
        self.acceptedNouns = ["noun.animal", "noun.artifact", "noun.food", "noun.plant", "noun.object"]
        self.bigramModel = None
        self.trigramModel = None
        self.paragraph = ""
        self.paragraphs = 4

        try:
            nltk.data.find('tokenizers/wordnet')
        except LookupError:
            nltk.download('wordnet')

        try:
            nltk.data.find('tokenizers/reuters')
        except LookupError:
            nltk.download('reuters')

        self.buildModels()

    def reset(self):
        self.inventory.clear()
        self.known_places.clear()
        self.known_people.clear()
        self.introduction = ""
        self.items_in_paragraph.clear()
        self.places_in_paragraph.clear()
        self.people_in_paragraph.clear()
        self.events_in_paragraph.clear()
        self.nouns_in_paragraph.clear()
        self.current_paragraphs = 0 # Tract current paractraph
        self.name = ""
        self.setting = ""
        self.setting_id = 0
        self.text = ""
        self.html = "<html><body>"
        self.HTML_END = "</body></html>"
        self.paragraph = ""
        self.paragraphs = 4

    def getSettings(self):
        return settings

    def getActionTemplates(self, action, entity):
        return self.actionTemplates.getTemplate(action, self.name, entity)

    def buildModels(self):
        #https://www.analyticsvidhya.com/blog/2019/08/comprehensive-guide-language-model-nlp-python-code/
        print("Building ngram models...")
        # Create a placeholder for model
        self.bigramModel = defaultdict(lambda: defaultdict(lambda: 0))
        self.trigramModel = defaultdict(lambda: defaultdict(lambda: 0))

        # Count frequency of co-occurance  
        for sentence in reuters.sents():
            for w1, w2, w3 in trigrams(sentence, pad_right=True, pad_left=True):
                self.trigramModel[(w1, w2)][w3] += 1
            for w1, w2 in bigrams(sentence, pad_right=True, pad_left=True):
                self.bigramModel[(w1)][w2] += 1
        
        # Let's transform the counts to probabilities
        for w1_w2 in self.trigramModel:
            total_count = float(sum(self.trigramModel[w1_w2].values()))
            for w3 in self.trigramModel[w1_w2]:
                self.trigramModel[w1_w2][w3] /= total_count

        for w1 in self.bigramModel:
            total_count = float(sum(self.bigramModel[w1].values()))
            for w2 in self.bigramModel[w1]:
                self.bigramModel[w1][w2] /= total_count
        print("Done building models")

    def getSentiment(self, text):
        analysis = TextBlob(text) 
        # set sentiment 
        if analysis.sentiment.polarity > 0: 
            return 'positive'
        elif analysis.sentiment.polarity == 0: 
            return 'neutral'
        else: 
            return 'negative'

    def splitSentences(self, textExtract, allowIncomplete=False):
        nlp2 = spacy.load("en_core_web_lg")
        nlp2.add_pipe(nlp2.create_pipe('sentencizer'), first=True)
        doc = nlp2(textExtract)
        sentences = [sent.string.strip() for sent in doc.sents]
        # Check completion
        result = []
        for sentence in sentences:
            doc = nlp2(sentence)
            if doc[len(doc)-1].is_punct or allowIncomplete:
                result.append(sentence)
        return result

    def truncateLastSentences(self, characters):
        sentences = self.splitSentences(self.text, False)
        result = ""
        for sentence in reversed(sentences):
            if (len(result) > characters):
                return result
            else:
                result = sentence + " " + result
        return result


    def generateText(self, history):
        text = self.gpt2.generate_text(history, 100)
        sentences = self.splitSentences(text, False)
        return " ".join(sentences)

    def generateEnd(self):
        ending_text = settings[self.setting].endings[self.setting_id]
        ending_text = ending_text.replace("[name]", self.name)
        html_ending = self.highlightEntities(ending_text)
        html_ending = html_ending.replace(self.name, "<b>" + self.name + "</b>")

        self.text = self.text + ending_text
        temp_html = self.html + "<span style=\"background-color: #FFFF00\">" + html_ending + "</span>"        
        self.html = self.html + html_ending
        return temp_html + self.HTML_END

    def extractEntities(self, text):
        # 4. NLP on paragraph [Extract People, Places, Items]
        doc = self.nlp(text)

        # 4.1 clear entities before extraction
        self.people_in_paragraph.clear()
        self.places_in_paragraph.clear()
        self.events_in_paragraph.clear()
        self.items_in_paragraph.clear()
        self.nouns_in_paragraph.clear()

        # 4.2 extract each entity
        for ent in doc.ents:
            if ent.label_ == "PERSON" and ent.text != self.name and not ent.text in self.people_in_paragraph:
                self.people_in_paragraph.append(ent.text)
            elif (ent.label_ == "GPE" or ent.label_ == "LOC") and not ent.text in self.places_in_paragraph:
                self.places_in_paragraph.append(ent.text)
            elif ent.label_ == "EVENT" and not ent.text in self.events_in_paragraph:  # talk about event
                self.events_in_paragraph.append(ent.text)
            elif ent.label_ == "PRODUCT" and not ent.text in self.items_in_paragraph:
                self.items_in_paragraph.append(ent.text)

        # Extract nouns
        if (self.USE_NOUNS):
            for token in doc:
                if token.pos_ == 'NOUN':

                    # Only allow man made objects
                    for synset in wn.synsets(token.text):
                        if ((synset.lexname() in self.acceptedNouns) and (not token.text in self.nouns_in_paragraph)):
                            print("type: " + synset.lexname() + " value: " + token.text)
                            self.nouns_in_paragraph.append(token.text)

    def highlightEntities(self, text):
        for person in self.people_in_paragraph:
            text = text.replace(person, "<b><font color=\"red\">" + person + "</font></b>")
        for place in self.places_in_paragraph:
            text = text.replace(place, "<b><font color=\"green\">" + place + "</font></b>")
        for event in self.events_in_paragraph:
            text = text.replace(event, "<b><font color=\"yellow\">" + event + "</font></b>")
        for item in self.items_in_paragraph:
            text = text.replace(item, "<b><font color=\"purple\">" + item + "</font></b>")

        # todo highlight from inventory?
        if (self.USE_NOUNS):
            for noun in self.nouns_in_paragraph:
                text = text.replace(noun, "<b><font color=\"blue\">" + noun + "</font></b>")
        return text