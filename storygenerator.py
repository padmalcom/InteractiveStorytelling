from collections import Counter, defaultdict
import operator
import random
import sys

# nlp
import spacy
import en_core_web_lg
import nltk
from nltk.corpus import brown, reuters
from nltk import bigrams, trigrams
from nltk.corpus import wordnet as wn
from textblob import TextBlob
import gender_guesser.detector as gender

# custom
from gpt2 import GPT2
from coherence import Coherence
from actiontemplates import ActionTemplates
from item import items
from setting import settings
from setting import coherence_phrases
from combination import combinations

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
        self.all_paragraphs = []
        self.name = ""
        self.party1 = "John"
        self.party2 = "Sally"
        self.setting = ""
        self.setting_id = 0
        self.text = ""
        self.html = "<html><body>"
        self.HTML_END = "</body></html>"
        self.gpt2 = GPT2(4)
        self.USE_NOUNS = True
        self.LIMIT_NOUNS_BY_SYNSETS = True
        self.MAX_ACTIONS = 4
        self.actionTemplates = ActionTemplates()
        #self.acceptedNouns = ["noun.animal", "noun.artifact", "noun.food", "noun.plant", "noun.object"] 
        self.acceptedNouns = ["noun.artifact"]
        self.paragraph = ""
        self.paragraphs = 6
        self.CHANCE_TO_REMEMBER_ITEM = 0.3
        self.CHANCE_TO_REMEMBER_PERSON = 0.7
        self.PRIORIZE_ITEM_USAGE = True
        self.PRIORIZE_COMBINATIONS = True
        self.PRIORIZE_DIALOG = True
        self.AVOID_SIMILAR_NOUNS = False # This one is buggy as hell
        self.TRUCATED_LAST_TEXT = 300
        self.gender = gender.Detector()
        self.coherence = Coherence()
        

        # try:
        #     nltk.data.find('tokenizers/wordnet')
        # except LookupError:
        #     nltk.download('wordnet')

        # try:
        #     nltk.data.find('tokenizers/brown')
        # except LookupError:
        #     nltk.download('brown')

        # try:
        #     nltk.data.find('tokenizers/reuters')
        # except LookupError:
        #     nltk.download('reuters')            

        # self.__buildNGramModels__()

        # # test
        # p1 = self.getVerbNounProbability("take", "apple")
        # p2 = self.getProbabilityNgram("takes an apple")
        # p3 = self.gpt2.score_probability("takes an apple")

        # print("p1 " + str(p1) + " p2 " + str(p2) + " p3 " + str(p3))

        # p11 = self.getVerbNounProbability("take", "car")
        # p12 = self.getProbabilityNgram("takes a car")
        # p13 = self.gpt2.score_probability("takes a car")

        # print("p11 " + str(p11) + " p12 " + str(p12) + " p13 " + str(p13))

        # p21 = self.getVerbNounProbability("push", "love")
        # p22 = self.getProbabilityNgram("pushes a love")
        # p23 = self.gpt2.score_probability("pushes a love")

        # print("p21 " + str(p21) + " p22 " + str(p22) + " p23 " + str(p23))        

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
        self.party1 = ""
        self.party2 = ""
        self.setting = ""
        self.setting_id = 0
        self.text = ""
        self.html = "<html><body>"
        self.HTML_END = "</body></html>"
        self.paragraph = ""
        self.paragraphs = 4
        self.all_paragraphs.clear()

    def getSettings(self):
        return settings

    def getActionTemplates(self, action, entity, entity_type):
        simpleaction, extaction = self.actionTemplates.getTemplate(action, self.name, entity, entity_type)
        return simpleaction, extaction

    def calculateParagraphCoherence(self):
        return self.coherence.calculateCoherence(self.all_paragraphs)

    def getProbability(self, sentence):
        return self.gpt2.score_probability(sentence)

    # def getVerbNounProbability(self, verb, noun):
    #     tokens = self.nlp(verb + " " + noun)
    #     return tokens[0].similarity(tokens[1])

    # def __buildNGramModels__(self):
    #     #https://www.analyticsvidhya.com/blog/2019/08/comprehensive-guide-language-model-nlp-python-code/
    #     print("Building ngram models...")
    #     # Create a placeholder for model
    #     self.bigramModel = defaultdict(lambda: defaultdict(lambda: 0))
    #     self.trigramModel = defaultdict(lambda: defaultdict(lambda: 0))

    #     # Count frequency of co-occurance  
    #     for sentence in reuters.sents():
    #         for w1, w2, w3 in trigrams(sentence, pad_right=True, pad_left=True):
    #             self.trigramModel[(w1, w2)][w3] += 1
    #         for w1, w2 in bigrams(sentence, pad_right=True, pad_left=True):
    #             self.bigramModel[(w1)][w2] += 1
        
    #     # Let's transform the counts to probabilities
    #     for w1_w2 in self.trigramModel:
    #         total_count = float(sum(self.trigramModel[w1_w2].values()))
    #         for w3 in self.trigramModel[w1_w2]:
    #             self.trigramModel[w1_w2][w3] /= total_count

    #     for w1 in self.bigramModel:
    #         total_count = float(sum(self.bigramModel[w1].values()))
    #         for w2 in self.bigramModel[w1]:
    #             self.bigramModel[w1][w2] /= total_count
    #     print("Done building models")

    # def getProbabilityNgram(self, sentence):
    #     doc = self.nlp(sentence)
    #     words = [token.text for token in doc if token.is_punct != True]
    #     if (len(words) < 2 or (len(words) > 3)):
    #         print("Ngram probability only supports 2 or 3 words. You entered " + str(len(words)) + "('" + sentence + "').")
    #         return 0.0
    #     else:
    #         if (len(words) == 2):
    #             prob = self.getProbabilityBigram(words[0], words[1])
    #             return prob
    #         else:
    #             prob = self.getProbabilityTrigram(words[0], words[1], words[2])
    #             return prob
    #     print("Here")
    #     return 0.0

    # def getProbabilityBigram(self, word1, word2):
    #     bigramDict = dict(self.bigramModel[word1])
    #     print("bigram for " + word1)
    #     print(bigramDict)
    #     if word2 in bigramDict:
    #         return bigramDict[word2]
    #     else:
    #         print("Not all words in dict 2 ")
    #         return 0.0

    # def getProbabilityTrigram(self, word1, word2, word3):
    #     trigramDict = dict(self.trigramModel[word1, word2])
    #     print("Trigram for " + word1 + " and " + word2)
    #     print(trigramDict)
    #     if word3 in trigramDict:
    #         return trigramDict[word3]
    #     else:
    #         print("Not all words in dict 3 ")
    #         return 0.0

    #def getSentiment(self, text):
    #    analysis = TextBlob(text) 
    #    if analysis.sentiment.polarity > 0: 
    #        return 'positive'
    #    elif analysis.sentiment.polarity == 0: 
    #        return 'neutral'
    #    else: 
    #        return 'negative'

    def splitSentences(self, textExtract, allowIncomplete=False):
        nlp2 = spacy.load("en_core_web_lg")
        nlp2.add_pipe(nlp2.create_pipe('sentencizer'), first=True)
        doc = nlp2(textExtract)
        sentences = [sent.string.strip() for sent in doc.sents]
        # Check completion
        result = []
        for sentence in sentences:
            doc = nlp2(sentence)
            if (len(doc)<=0):
                continue
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
        
    def replaceGenderTokens(self, sentences, name):
        g = self.gender.get_gender(name)
        hisher = ""
        heshe = ""
        if (g == "unknown" or g == "androgynous" or g == "male" or g == "mostly_male"):
            hisher = "his"
            heshe = "he"
        else:
            hisher = "her"
            heshe = "she"
            
        s = sentences.replace("[hisher]", hisher)
        s = s.replace("[heshe]", heshe)
        return s

    def generateText(self, history):
        text = self.gpt2.generate_text(history, 100)
        sentences = self.splitSentences(text, False)
        # Add information about existing item
        addinfo = ""
        p = random.randint(0, 100) / 100.0
        if p <= self.CHANCE_TO_REMEMBER_ITEM and len(self.inventory) > 0:
            item = random.choice(self.inventory)
            addinfo = "In that particular moment, " + self.name + " remembered [heshe] had a " + item + " in [hisher] pocket."
            addinfo = self.replaceGenderTokens(addinfo, self.name)
            sentences.append(addinfo)
        
        p = random.randint(0, 100) / 100.0
        if p <= self.CHANCE_TO_REMEMBER_PERSON and (self.party1 != "" or self.party2 != ""):
            addpersoninfo = random.choice(coherence_phrases)
            
            rndPerson = -1
            if (self.party1 == "" and self.party2 != ""):
                rndPerson = 1
            elif (self.party1 != "" and self.party2 == ""):
                rndPerson = 0
            else:
                rndPerson = random.randint(0, 1)

            if rndPerson > -1:
                if (rndPerson == 0 and addpersoninfo.find("[person]") > -1):
                    addpersoninfo = addpersoninfo.replace("[person]", self.party1)
                    addpersoninfo = self.replaceGenderTokens(addpersoninfo, self.party1)          
                if (rndPerson == 1 and addpersoninfo.find("[person]") > -1):
                    addpersoninfo = addpersoninfo.replace("[person]", self.party2)
                    addpersoninfo = self.replaceGenderTokens(addpersoninfo, self.party2)
                sentences.append(addpersoninfo)
        
        return " ".join(sentences)

    def generateEnd(self):
        print("End reached")
        ending_text = settings[self.setting].endings[self.setting_id]
        ending_text = ending_text.replace("[name]", self.name)
        html_ending = self.highlightEntities(ending_text)
        html_ending = html_ending.replace(self.name, "<b>" + self.name + "</b>")

        self.text = self.text + ending_text
        temp_html = self.html + "<span style=\"background-color: #FFFF00\">" + html_ending + "</span>"        
        self.html = self.html + html_ending
        return temp_html

    def extractEntities(self, text):
        # 4. NLP on paragraph [Extract People, Places, Items]
        doc = self.nlp(text)

        # 4.1 clear entities before extraction
        self.people_in_paragraph.clear()
        self.places_in_paragraph.clear()
        self.events_in_paragraph.clear()
        self.items_in_paragraph.clear()
        self.nouns_in_paragraph.clear()

        entity_ids = {}

        # 4.2 extract each entity
        for ent in doc.ents:
            if (ent.kb_id_ in entity_ids.keys() and self.AVOID_SIMILAR_NOUNS):
                print("Will not add entity " + ent.text + " because it is similar to " + entity_ids[ent.kb_id_] + ".")
                continue

            if (ent.label_ == "PERSON") and (ent.text != self.name) and (not ent.text in self.people_in_paragraph):
                self.people_in_paragraph.append(ent.text)
                entity_ids[ent.kb_id_] = ent.text                    
            elif (ent.label_ == "GPE" or ent.label_ == "LOC") and (not ent.text in self.places_in_paragraph):
                self.places_in_paragraph.append(ent.text)  
                entity_ids[ent.kb_id_] = ent.text          
            elif (ent.label_ == "EVENT") and (not ent.text in self.events_in_paragraph):  # talk about event
                self.events_in_paragraph.append(ent.text)
                entity_ids[ent.kb_id_] = ent.text
            elif (ent.label_ == "PRODUCT") and (not ent.text in self.items_in_paragraph):
                self.items_in_paragraph.append(ent.text)
                entity_ids[ent.kb_id_] = ent.text

        # Extract nouns
        if (self.USE_NOUNS):
            for token in doc:
                if token.pos_ == 'NOUN':

                    # Only allow man made objects
                    if (self.LIMIT_NOUNS_BY_SYNSETS == False) and (not token.text in self.nouns_in_paragraph):
                        print("Adding noun " + token.text + " anyway since we ignore synset matching.")
                        self.nouns_in_paragraph.append(token.text)

                    else:
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

    def generateActions(self):
        all_actions = []

        for person in self.people_in_paragraph:
            simple_action, action_sentence = self.getActionTemplates("talk to", person, "PERSON")
            probability = self.getProbability(simple_action)
            if self.PRIORIZE_DIALOG:
                probability = -sys.float_info.max
            all_actions.append({"type":"person", "action":"talk to", "entity":person, "sentence":action_sentence, "simple": simple_action, "probability":probability})

        for _, combination in combinations.items():
            contains_all_items = all(elem in self.inventory for elem in [i.name for i in combination.items])
            if (contains_all_items):                 
                action_sentence = combination.action
                action_sentence = action_sentence.replace("[name]", self.name)
                simple_action = combination.simple_action
                probability = self.getProbability(action_sentence)
                if self.PRIORIZE_COMBINATIONS:
                    probability = -sys.float_info.max
                all_actions.append({"type":"combination", "action":"combine", "entity":combination.returnItem.name, "sentence":action_sentence, "simple": simple_action, "probability":probability})

        for person in self.people_in_paragraph:
            actions = ["compliment", "insult", "look at", "who are you,"]
            for action in actions:
                simple_action, action_sentence = self.getActionTemplates(action, person, "PERSON")
                probability = self.getProbability(simple_action)
                all_actions.append({"type":"person", "action":action, "entity":person, "sentence":action_sentence, "simple": simple_action, "probability":probability})

        for item in self.inventory:
            print("item in inv: " + item)
            simple_action, action_sentence = self.getActionTemplates("use", item, "ITEM")
            probability = self.getProbability(simple_action)
            if self.PRIORIZE_ITEM_USAGE:
                probability = -sys.float_info.max            
            all_actions.append({"type":"item_from_inventory", "action":"use", "entity":item, "sentence":action_sentence, "simple": simple_action, "probability":probability})
            print(all_actions[-1])

        for place in self.places_in_paragraph:
            actions = ["go to", "look at"]
            for action in actions:                  
                simple_action, action_sentence = self.getActionTemplates(action, place, "PLACE")
                probability = self.getProbability(simple_action)
                all_actions.append({"type":"place", "action":action, "entity":place, "sentence":action_sentence, "simple": simple_action, "probability":probability})

        for event in self.events_in_paragraph:
            actions = ["think about"]
            for action in actions:
                simple_action, action_sentence = self.getActionTemplates(action, event, "EVENT")
                probability = self.getProbability(simple_action)
                all_actions.append({"type":"event", "action":action, "entity":event, "sentence":action_sentence, "simple": simple_action, "probability":probability})

        for item in self.items_in_paragraph:
            actions = ["take", "use", "push"]
            for action in actions:
                simple_action, action_sentence = self.getActionTemplates(action, item, "ITEM")
                probability = self.getProbability(simple_action)
                all_actions.append({"type":"item", "action":action, "entity":item, "sentence":action_sentence, "simple": simple_action, "probability":probability})

        if (self.USE_NOUNS):
            for noun in self.nouns_in_paragraph:
                actions = ["take", "use", "push", "pull", "open", "close", "look at", "talk to"]
                for action in actions:
                    simple_action, action_sentence = self.getActionTemplates(action, noun, "NOUN")
                    probability = self.getProbability(simple_action)
                    all_actions.append({"type":"noun", "action":action, "entity":noun, "sentence":action_sentence, "simple": simple_action, "probability":probability})

        print("Found " + str(len(all_actions)) + " actions.")
        sorted_actions = sorted(all_actions, key=operator.itemgetter("probability"))

        if (self.MAX_ACTIONS > -1):
            sorted_actions = sorted_actions[:self.MAX_ACTIONS]

        return sorted_actions