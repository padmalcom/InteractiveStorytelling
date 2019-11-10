from item import items
from combination import combinations
from setting import settings
from functools import partial
import random
import spacy
import en_core_web_lg
from gpt2 import GPT2
from textblob import TextBlob
import os
from actiontemplates import ActionTemplates
from nltk.corpus import wordnet as wn
import nltk
from nltk import ngrams

# pyqt5
from PyQt5 import QtCore, QtGui, QtWidgets
import sys

# Todo
# - Check if model already exists
# - Add checkbox for model
# - Add "generate twine story"

# QT window
class InteractiveStoryUI(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(794, 600)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame = QtWidgets.QFrame(Dialog)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.gridLayout = QtWidgets.QGridLayout(self.frame)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(self.frame)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.comboBox = QtWidgets.QComboBox(self.frame)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.gridLayout.addWidget(self.comboBox, 0, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.frame)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 0, 2, 1, 1)
        self.lineEdit = QtWidgets.QLineEdit(self.frame)
        self.lineEdit.setObjectName("lineEdit")
        self.gridLayout.addWidget(self.lineEdit, 0, 3, 1, 1)
        self.pushButton_2 = QtWidgets.QPushButton(self.frame)
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.clicked.connect(self.startNewGame)
        self.gridLayout.addWidget(self.pushButton_2, 0, 4, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.frame)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.spinBox = QtWidgets.QSpinBox(self.frame)
        self.spinBox.setMinimum(1)
        self.spinBox.setMaximum(2000)
        self.spinBox.setObjectName("spinBox")
        self.gridLayout.addWidget(self.spinBox, 1, 1, 1, 1)
        self.pushButton = QtWidgets.QPushButton(self.frame)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 1, 4, 1, 1)
        self.verticalLayout.addWidget(self.frame)
        self.textEdit = QtWidgets.QTextEdit(Dialog)
        self.textEdit.setObjectName("textEdit")
        self.verticalLayout.addWidget(self.textEdit)
        self.frame_2 = QtWidgets.QFrame(Dialog)
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.frame_2)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.groupBox = QtWidgets.QGroupBox(self.frame_2)
        self.groupBox.setMinimumSize(QtCore.QSize(500, 100))
        self.groupBox.setObjectName("groupBox")
        self.groupBoxGridLayout = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_2.addWidget(self.groupBox, 0, 0, 1, 1)
        self.groupBox_2 = QtWidgets.QGroupBox(self.frame_2)
        self.groupBox_2.setMinimumSize(QtCore.QSize(250, 100))
        self.groupBox_2.setObjectName("groupBox_2")
        self.groupBox_2GridLayout = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout_2.addWidget(self.groupBox_2, 0, 1, 1, 1)
        self.verticalLayout.addWidget(self.frame_2)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Interactive Storytelling"))
        self.label.setText(_translate("Dialog", "Setting:"))

        allSettings = list(settings.keys())
        for i,s in enumerate(allSettings):
            self.comboBox.setItemText(i, _translate("Dialog", s))
        self.label_3.setText(_translate("Dialog", "Player name:"))
        self.pushButton_2.setText(_translate("Dialog", "Start game"))
        self.label_2.setText(_translate("Dialog", "Paragraphs:"))
        self.pushButton.setText(_translate("Dialog", "Quit"))
        self.textEdit.setHtml(_translate("Dialog", self.html + self.html_end))
        self.groupBox.setTitle(_translate("Dialog", "Actions"))
        self.groupBox_2.setTitle(_translate("Dialog", "Inventory"))
        self.lineEdit.setText(_translate("Dialog", "Jim"))
        self.spinBox.setValue(4)

    def __init__(self):
        super().__init__()
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
        self.paragraph_count = 0
        self.name = ""
        self.setting = ""
        self.setting_id = 0
        self.text = ""
        self.html = "<html><body>"
        self.html_end = "</body></html>"
        self.action_buttons = []
        self.gpt2 = GPT2()
        self.USE_NOUNS = True
        self.MAX_ACTIONS = 18
        self.actionTemplates = ActionTemplates()
        self.acceptedNouns = ["noun.animal", "noun.artifact", "noun.food", "noun.plant", "noun.object"]

        # gpt adventure
        self.STRICT_MODE = True
        self.alreadyDone = ""
        self.locContext = ""

        #nltk.download('wordnet')

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

    def trucateLastSentences(self, textExtract, characters):
        sentences = self.splitSentences(textExtract, False)
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
        ending_text = settings["harry potter"].endings[self.setting_id]
        ending_text = ending_text.replace("[name]", self.name)
        html_ending = self.highlightEntities(ending_text)
        html_ending = html_ending.replace(self.name, "<b>" + self.name + "</b>")

        self.text = self.text + ending_text
        temp_html = self.html + "<span style=\"background-color: #FFFF00\">" + html_ending + "</span>"        
        self.html = self.html + html_ending
        ui.textEdit.setHtml(temp_html + self.html_end)

    def clickAction(self, action, entity):

        # If no action is defined, just continue on the last text block.
        if (action == "" and entity == ""):
            action_sentence = ""
        else:
            # Select action template
            action_sentence = self.actionTemplates.getTemplate(action, self.name, entity)

        if self.paragraph_count < self.paragraphs:

            self.text = self.text + " " + action_sentence

            # generate next paragraph
            trucated_text = self.trucateLastSentences(self.text, 200)
            new_text = self.generateText(trucated_text)
            self.paragraph = action_sentence + " " + new_text

            # extract entities
            self.extractEntities()

            self.html_paragraph = self.paragraph

            # 5.1 Clean up buttons
            self.createButtons()

            # highlight player name
            self.html_paragraph = self.highlightEntities(self.html_paragraph)
            self.html_paragraph = self.html_paragraph.replace(self.name, "<b>" + self.name + "</b>")

            # append html and text
            self.text = self.text + " " + self.paragraph
            temp_html = self.html + " <span style=\"background-color: #FFFF00\">" + self.html_paragraph + "</span>"
            self.html = self.html + " " + self.html_paragraph
            ui.textEdit.setHtml(temp_html + self.html_end)

            self.paragraph_count +=1
        else:
            self.generateEnd()

    def extractEntities(self):
        # 4. NLP on paragraph [Extract People, Places, Items]
        doc = self.nlp(self.paragraph)

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

        if (self.USE_NOUNS):
            for noun in self.nouns_in_paragraph:
                text = text.replace(noun, "<b><font color=\"blue\">" + noun + "</font></b>")
        return text

    def createButtons(self):

        # Todo rate ngrams
        # https://stackoverflow.com/questions/54962539/how-to-get-the-probability-of-bigrams-in-a-text-of-sentences
        # https://stackoverflow.com/questions/6462709/nltk-language-model-ngram-calculate-the-prob-of-a-word-from-context
        sequence = nltk.tokenize.word_tokenize("Take shirt") 
        bigram = ngrams(sequence,2)
        freq_dist = nltk.FreqDist(bigram)
        prob_dist = nltk.MLEProbDist(freq_dist)
        number_of_bigrams = freq_dist.N()
        print ("Probability of take shirt: " + str(prob_dist) + " number: " + str(number_of_bigrams))


        # 5.2 Are there any buttons? Destroy
        for button in self.action_buttons:
            self.groupBoxGridLayout.removeWidget(button)
            button.deleteLater()
            button = None
        self.action_buttons.clear()

        # 5.3 Check if there are any actions
        if (len(self.people_in_paragraph) > 0 or len(self.places_in_paragraph) > 0 or
            len(self.events_in_paragraph) > 0 or len(self.items_in_paragraph) > 0 or
            (len(self.nouns_in_paragraph) > 0 and self.USE_NOUNS)):

            # 6. Generate actions [Talk to, Take [item] {based on nlp}, go to [Place], Inspect [Item, Place, Person, Item in inventory], Push, Pull {fun?},
            # insult/compliment [Person], use [item], combine [item, item]]
            action_count = 0
            for person in self.people_in_paragraph:
                actions = ["compliment", "insult", "look at", "who are you,"]
                for action in actions:
                    if self.MAX_ACTIONS > -1 and action_count == self.MAX_ACTIONS-1:
                        break
                    else:
                        self.action_buttons.append(QtWidgets.QPushButton(self.groupBox))
                        self.action_buttons[-1].setText(action + " " + person)
                        self.groupBoxGridLayout.addWidget(self.action_buttons[-1], (len(self.action_buttons)-1) // 3, (len(self.action_buttons)-1) % 3)
                        self.action_buttons[-1].setToolTip(action + " " + person)                    
                        self.action_buttons[-1].clicked.connect(partial(self.clickAction, action, person))
                        action_count +=1

            for place in self.places_in_paragraph:
                actions = ["go to", "look at"]
                for action in actions:
                    if self.MAX_ACTIONS > -1 and action_count == self.MAX_ACTIONS-1:
                        break
                    else:                    
                        self.action_buttons.append(QtWidgets.QPushButton(self.groupBox))
                        self.action_buttons[-1].setText(action + " " + place)
                        self.groupBoxGridLayout.addWidget(self.action_buttons[-1], (len(self.action_buttons)-1) // 3, (len(self.action_buttons)-1) % 3)
                        self.action_buttons[-1].setToolTip(action + " " + place)                    
                        self.action_buttons[-1].clicked.connect(partial(self.clickAction, action, place))
                        action_count +=1

            for event in self.events_in_paragraph:
                actions = ["think about"]
                for action in actions:
                    if self.MAX_ACTIONS > -1 and action_count == self.MAX_ACTIONS-1:
                        break
                    else:
                        self.action_buttons.append(QtWidgets.QPushButton(self.groupBox))
                        self.action_buttons[-1].setText(action + " " + event)
                        self.groupBoxGridLayout.addWidget(self.action_buttons[-1], (len(self.action_buttons)-1) // 3, (len(self.action_buttons)-1) % 3)
                        self.action_buttons[-1].setToolTip(action + " " + event)                    
                        self.action_buttons[-1].clicked.connect(partial(self.clickAction, action, event))
                        action_count +=1

            for item in self.items_in_paragraph:
                actions = ["take", "use", "push"]
                for action in actions:
                    if self.MAX_ACTIONS > -1 and action_count == self.MAX_ACTIONS-1:
                        break
                    else:
                        self.action_buttons.append(QtWidgets.QPushButton(self.groupBox))
                        self.action_buttons[-1].setText(action + " " + item)
                        self.groupBoxGridLayout.addWidget(self.action_buttons[-1], (len(self.action_buttons)-1) // 3, (len(self.action_buttons)-1) % 3)
                        self.action_buttons[-1].setToolTip(action + " " + item)                    
                        self.action_buttons[-1].clicked.connect(partial(self.clickAction, action, item))
                        action_count +=1

            if (self.USE_NOUNS):
                for noun in self.nouns_in_paragraph:
                    actions = ["take", "use", "push", "pull", "open", "close", "look at", "talk to"]
                    for action in actions:
                        if self.MAX_ACTIONS > -1 and action_count == self.MAX_ACTIONS-1:
                            break
                        else:
                            self.action_buttons.append(QtWidgets.QPushButton(self.groupBox))
                            self.action_buttons[-1].setText(action + " " + noun)
                            self.groupBoxGridLayout.addWidget(self.action_buttons[-1], (len(self.action_buttons)-1) // 3, (len(self.action_buttons)-1) % 3)
                            self.action_buttons[-1].setToolTip(action + " " + noun)                    
                            self.action_buttons[-1].clicked.connect(partial(self.clickAction, action, noun))
                            action_count +=1


        # 6.2 Continue without taking an action 
        self.action_buttons.append(QtWidgets.QPushButton(self.groupBox))
        self.action_buttons[-1].setText("continue")
        self.groupBoxGridLayout.addWidget(self.action_buttons[-1], (len(self.action_buttons)-1) // 3, (len(self.action_buttons)-1) % 3)
        self.action_buttons[-1].setToolTip("continue")
        self.action_buttons[-1].clicked.connect(partial(self.clickAction, "", ""))

    def startNewGame(self):
        self.html = ""
        self.html_paragraph = ""
        self.paragraph = ""
        self.paragraph_count = 0
        self.people_in_paragraph.clear()
        self.places_in_paragraph.clear()
        self.events_in_paragraph.clear()
        self.items_in_paragraph.clear()
        self.nouns_in_paragraph.clear()

        ui.textEdit.setHtml(
            self.html + "<b>Welcome to PCG adventures!</b>" + self.html_end)

        # 1. Enter name and story length [# of paragraphs]
        self.name = self.lineEdit.text()
        self.paragraphs = self.spinBox.value()

        # 2. Select setting [middle age, fantasy, horror]
        self.setting = self.comboBox.currentText()

        # 3. Load/generate introduction [Place, Time, Crew, Items]
        # -> place items in first place.
        self.setting_id = random.randrange(0, len(settings["harry potter"].introductions))
        self.setting_id = 0 # temporary
        self.paragraph = settings["harry potter"].introductions[self.setting_id]

        if self.paragraph_count < self.paragraphs:

            # Replace [name]
            self.paragraph = self.paragraph.replace("[name]", self.name)

            self.extractEntities()

            # temporary element to be appended to html and text
            self.html_paragraph = self.paragraph

            # 5.1 Clean up buttons and create new
            self.createButtons()

            # Highlight entities
            self.html_paragraph = self.highlightEntities(self.html_paragraph)

            # append paragraph
            self.text = self.text + " " + self.paragraph

            # highlight player name
            self.html_paragraph = self.html_paragraph.replace(self.name, "<b>" + self.name + "</b>")

            # append html and highlight
            temp_html = self.html + " <span style=\"background-color: #FFFF00\">" + self.html_paragraph + "</span>"
            self.html = self.html + " " + self.html_paragraph
            ui.textEdit.setHtml(temp_html + self.html_end)

            # 11. Increase paragraph counter
            self.paragraph_count += 1

        else:
            self.generateEnd()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = InteractiveStoryUI()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
