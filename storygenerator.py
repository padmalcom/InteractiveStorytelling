from collections import Counter, defaultdict
import operator
import random
import sys

# nlp
import spacy
import en_core_web_lg
import nltk
from nltk.corpus import brown
from nltk import bigrams, trigrams
from nltk.corpus import wordnet as wn
from textblob import TextBlob

# custom
from gpt2 import GPT2
from actiontemplates import ActionTemplates
from item import items
from setting import settings
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
        self.name = ""
        self.setting = ""
        self.setting_id = 0
        self.text = ""
        self.html = "<html><body>"
        self.HTML_END = "</body></html>"
        self.gpt2 = GPT2(dummy=False)
        self.USE_NOUNS = True
        self.MAX_ACTIONS = 2
        self.actionTemplates = ActionTemplates()
        self.acceptedNouns = ["noun.animal", "noun.artifact", "noun.food", "noun.plant", "noun.object"] 
        self.bigramModel = None
        self.trigramModel = None
        self.paragraph = ""
        self.paragraphs = 6
        self.CHANCE_TO_REMEMBER_ITEM = 0.3
        self.PRIORIZE_ITEM_USAGE = True
        self.PRIORIZE_COMBINATIONS = True

        try:
            nltk.data.find('tokenizers/wordnet')
        except LookupError:
            nltk.download('wordnet')

        try:
            nltk.data.find('tokenizers/brown')
        except LookupError:
            nltk.download('brown')

        #self.__buildNGramModels__()

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
        simpleaction, extaction = self.actionTemplates.getTemplate(action, self.name, entity)
        return simpleaction, extaction

    def getProbability(self, sentence):
        return self.gpt2.score_probability(sentence)

    def getVerbNounProbability(self, verb, noun):
        #nlp = spacy.load("en_core_web_lg")
        tokens = self.nlp(verb + " " + noun)
        return tokens[0].similarity(tokens[1])

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


    def generateText(self, history):
        text = self.gpt2.generate_text(history, 100)
        sentences = self.splitSentences(text, False)
        # Add information about existing item
        addinfo = ""
        p = random.randint(0, 100) / 100.0
        if p <= self.CHANCE_TO_REMEMBER_ITEM and len(self.inventory) > 0:
            item = random.choice(self.inventory)
            addinfo = "In that particular moment, " + self.name + " remembered he had a " + item + " in his pocket."
        return " ".join(sentences) + " " + addinfo

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
            if (ent.kb_id_ in entity_ids.keys()):
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

        for _, combination in combinations.items():
            contains_all_items = all(elem in self.inventory for elem in [i.name for i in combination.items])
            if (contains_all_items):                 
                action_sentence = combination.action
                action_sentence = action_sentence.replace("[name]", self.name)
                simple_action = combination.simple_action
                probability = self.getProbability(action_sentence)
                if self.PRIORIZE_COMBINATIONS:
                    probability = -sys.float_info.max
                #probability = self.getProbability(action_sentence)
                #probability = self.getVerbNounProbability(action, place) # 
                all_actions.append({"type":"combination", "action":"combine", "entity":combination.returnItem.name, "sentence":action_sentence, "simple": simple_action, "probability":probability})

        for item in self.inventory:
            print("item in inv: " + item)
            simple_action, action_sentence = self.getActionTemplates("use", item)
            probability = self.getProbability(simple_action)
            if self.PRIORIZE_ITEM_USAGE:
                probability = -sys.float_info.max            
            #probability = self.getProbability(action_sentence)
            #probability = self.getVerbNounProbability(action, item)
            all_actions.append({"type":"item_from_inventory", "action":"use", "entity":item, "sentence":action_sentence, "simple": simple_action, "probability":probability})
            print(all_actions[-1])


        for person in self.people_in_paragraph:
            actions = ["compliment", "insult", "look at", "who are you,"]
            for action in actions:
                simple_action, action_sentence = self.getActionTemplates(action, person)
                probability = self.getProbability(simple_action)
                #probability = self.getProbability(action_sentence)
                #probability = self.getVerbNounProbability(action, person)
                all_actions.append({"type":"person", "action":action, "entity":person, "sentence":action_sentence, "simple": simple_action, "probability":probability})

        for place in self.places_in_paragraph:
            actions = ["go to", "look at"]
            for action in actions:                  
                simple_action, action_sentence = self.getActionTemplates(action, place)
                probability = self.getProbability(simple_action)
                #probability = self.getProbability(action_sentence)
                #probability = self.getVerbNounProbability(action, place)
                all_actions.append({"type":"place", "action":action, "entity":place, "sentence":action_sentence, "simple": simple_action, "probability":probability})

        for event in self.events_in_paragraph:
            actions = ["think about"]
            for action in actions:
                simple_action, action_sentence = self.getActionTemplates(action, event)
                probability = self.getProbability(simple_action)
                #probability = self.getProbability(action_sentence)
                #probability = self.getVerbNounProbability(action, event)
                all_actions.append({"type":"event", "action":action, "entity":event, "sentence":action_sentence, "simple": simple_action, "probability":probability})

        for item in self.items_in_paragraph:
            actions = ["take", "use", "push"]
            for action in actions:
                simple_action, action_sentence = self.getActionTemplates(action, item)
                probability = self.getProbability(simple_action)
                #probability = self.getProbability(action_sentence)
                #probability = self.getVerbNounProbability(action, item)
                all_actions.append({"type":"item", "action":action, "entity":item, "sentence":action_sentence, "simple": simple_action, "probability":probability})

        if (self.USE_NOUNS):
            for noun in self.nouns_in_paragraph:
                actions = ["take", "use", "push", "pull", "open", "close", "look at", "talk to"]
                for action in actions:
                    simple_action, action_sentence = self.getActionTemplates(action, noun)
                    probability = self.getProbability(simple_action)
                    #probability = self.getProbability(action_sentence)
                    #probability = self.getVerbNounProbability(action, noun)
                    all_actions.append({"type":"noun", "action":action, "entity":noun, "sentence":action_sentence, "simple": simple_action, "probability":probability})

        print("Found " + str(len(all_actions)) + " actions.")
        sorted_actions = sorted(all_actions, key=operator.itemgetter("probability"))

        if (self.MAX_ACTIONS > -1):
            sorted_actions = sorted_actions[:self.MAX_ACTIONS]

        return sorted_actions