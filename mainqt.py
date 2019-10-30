from item import items
from combination import combinations
from setting import settings
from functools import partial
import random
import spacy
import en_core_web_lg
import gpt_2_simple as gpt2
import os

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
        self.comboBox.setItemText(0, _translate("Dialog", "fantasy"))
        self.comboBox.setItemText(1, _translate("Dialog", "sci-fy"))
        self.label_3.setText(_translate("Dialog", "Player name:"))
        self.pushButton_2.setText(_translate("Dialog", "Start game"))
        self.label_2.setText(_translate("Dialog", "Paragraphs:"))
        self.pushButton.setText(_translate("Dialog", "Quit"))
        self.textEdit.setHtml(_translate("Dialog", self.html + self.html_end))
        self.groupBox.setTitle(_translate("Dialog", "Actions"))
        self.groupBox_2.setTitle(_translate("Dialog", "Inventory"))
        self.lineEdit.setText(_translate("Dialog", "Jim"))
        self.spinBox.setValue(2)

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
        self.paragraph_count = 0
        self.name = ""
        self.setting = ""
        self.text = ""
        self.html = "<html><body>"
        self.html_end = "</body></html>"
        self.action_buttons = []
        if not os.path.isdir("./models/124M"):
            gpt2.download_gpt2(model_name="124M")
        self.session = gpt2.start_tf_sess()
        gpt2.load_gpt2(self.session, model_name="124M")

        # gpt adventure
        self.STRICT_MODE = True
        self.alreadyDone = ""
        self.locContext = ""

    def isContext(self, currentText): #is a iece of textthis a context change? (i.e. moving to a new room)
        if "you are" in currentText or "we are" in currentText or "this is" in currentText or '''you're''' in currentText: #context change
            return True
        else:
            return False

    def isInvalidMove(self, playerAction, result): #gpt is trying to move the player when they didn't specify they wanted to move
        if ("go ") in playerAction:
            return False
        else:
            if self.isContext(result):
                return True
            else:
                return False

    def isTakeLoop(self, playerAction, result): #lets us detect a loop condition where the game just replies "taken" or "done" to everything
        if "done" in result.lower() or ( "take" in result.lower() and "take" not in playerAction.lower()):
            return True
        else:
            return False

    def generateText(self, history, action):
        gpo=gpt2.generate(self.session, temperature=0.1,prefix=history, model_name="124M",length=100,return_as_list=True,nsamples=3,batch_size=3,top_p=0.99)
        for candidate in gpo:
            goodCandidate=False
            result=candidate
            sentences=result.split("\n")
            newprompt=""
            hasContext=False
            for sentence in sentences:
                words=sentence.split(" ")
                if (sentence not in self.alreadyDone or len(words) <= 2) and sentence not in newprompt and (self.isTakeLoop(action,sentence)==False) and (self.isInvalidMove(action,sentence)==False):#avoid repeating things we've said in this or previous responses. If a response is very short (i.e. "taken" when you pick up an item) it's ok to repeat.
                    if ("." in sentence or "?" in sentence or "!" in sentence) and (hasContext==False or self.isContext(sentence)==False) : #If it's a next player action, then stop, otherwise keep going
                        newprompt=newprompt+sentence
                        goodCandidate=True
                    if self.isContext(sentence):
                        hasContext=True
                    else:
                        if goodCandidate and self.STRICT_MODE: #This prevents GPT from taking actions on our behalf. If strict mode is on actions are never taken, if it is off they are taklen but not shown to us. Strict mode on can make the game more playable at the expense of less interesting descriptions 
                            break
            if goodCandidate:
                break
            if len(newprompt) > 3: #this will be blank if GPT couldn't come up with anything
                if self.isContext(newprompt): #This is updating the location context
                    self.locContext=newprompt
                self.alreadyDone=self.alreadyDone+newprompt+"\n"
                return newprompt.replace(".","\n")
            else:
                self.alreadyDone=self.alreadyDone+"\n"+action
                return "I don't know what to to."

    def generateEnd(self):
        ui.textEdit.setHtml(self.html + " The End " + self.html_end)

    def clickAction(self, action):
        ui.textEdit.setHtml(self.html + action + self.html_end)
        if self.paragraph_count < self.paragraphs:

            # Todo: highlight NER in html
            self.text = self.text + action
            self.html = self.html + action

            # extend action by gpt-2

            # add to text

            # truncate and generate new text

            self.extractEntities()
            self.html_paragraph = self.paragraph

            # 5.1 Clean up buttons

            self.createButtons()

            # append paragraph
            self.text = self.text + self.paragraph

            # highlight player name
            self.html_paragraph = self.html_paragraph.replace(self.name, "<b>" + self.name + "</b>")

            # append html and highlight
            self.html = self.html + self.html_paragraph
            ui.textEdit.setHtml(self.html + self.html_end)
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

        # 4.2 extract each entity
        for ent in doc.ents:
            print(ent.text, ent.start_char, ent.end_char, ent.label_)
            if ent.label_ == "PERSON" and ent.text != self.name and not ent.text in self.people_in_paragraph:
                self.people_in_paragraph.append(ent.text)
            elif (ent.label_ == "GPE" or ent.label_ == "LOC") and not ent.text in self.places_in_paragraph:
                self.places_in_paragraph.append(ent.text)
            elif ent.label_ == "EVENT" and not ent.text in self.events_in_paragraph:  # talk about event
                self.events_in_paragraph.append(ent.text)
            elif ent.label_ == "PRODUCT" and not ent.text in self.items_in_paragraph:
                self.items_in_paragraph.append(ent.text)

    def createButtons(self):
        # 5.2 Are there any buttons? Destroy
        for button in self.action_buttons:
            self.groupBoxGridLayout.removeWidget(button)
            button.deleteLater()
            button = None

        # 5.3 Check if there are any actions
        if (len(self.people_in_paragraph) > 0 or len(self.places_in_paragraph) > 0 or
            len(self.events_in_paragraph) > 0 or len(self.items_in_paragraph) > 0):

            # 6. Generate actions [Talk to, Take [item] {based on nlp}, go to [Place], Inspect [Item, Place, Person, Item in inventory], Push, Pull {fun?},
            # insult/compliment [Person], use [item], combine [item, item]]
            for person in self.people_in_paragraph:
                print("Processing person %s"%person)

                # Create buttons
                self.action_buttons.append(QtWidgets.QPushButton())
                self.action_buttons[-1].setText("Talk to " + person)
                self.action_buttons[-1].setToolTip("Talk to " + person)                    
                self.action_buttons[-1].clicked.connect(partial(self.clickAction, "Talk to " + person))
                self.groupBoxGridLayout.addWidget(self.action_buttons[-1], (len(self.action_buttons)-1) // 3, (len(self.action_buttons)-1) % 3)

                self.action_buttons.append(QtWidgets.QPushButton(self.groupBox))
                self.action_buttons[-1].setText("Look at " + person)
                self.groupBoxGridLayout.addWidget(self.action_buttons[-1], (len(self.action_buttons)-1) // 3, (len(self.action_buttons)-1) % 3)
                self.action_buttons[-1].setToolTip("Look at " + person)                    
                self.action_buttons[-1].clicked.connect(partial(self.clickAction, "Look at " + person))                        

                self.action_buttons.append(QtWidgets.QPushButton(self.groupBox))
                self.action_buttons[-1].setText("Insult " + person)
                self.groupBoxGridLayout.addWidget(self.action_buttons[-1], (len(self.action_buttons)-1) // 3, (len(self.action_buttons)-1) % 3)    
                self.action_buttons[-1].setToolTip("Insult " + person)                    
                self.action_buttons[-1].clicked.connect(partial(self.clickAction,"Insult " + person))                                
                
                self.action_buttons.append(QtWidgets.QPushButton(self.groupBox))
                self.action_buttons[-1].setText("Compliment " + person)
                self.groupBoxGridLayout.addWidget(self.action_buttons[-1], (len(self.action_buttons)-1) // 3, (len(self.action_buttons)-1) % 3)
                self.action_buttons[-1].setToolTip("Compliment" + person)                    
                self.action_buttons[-1].clicked.connect(partial(self.clickAction,"Compliment " + person))                        

                self.action_buttons.append(QtWidgets.QPushButton(self.groupBox))
                self.action_buttons[-1].setText(person + ", who are you?")
                self.groupBoxGridLayout.addWidget(self.action_buttons[-1], (len(self.action_buttons)-1) // 3, (len(self.action_buttons)-1) % 3)    
                self.action_buttons[-1].setToolTip(person + ", who are you?")                    
                self.action_buttons[-1].clicked.connect(partial(self.clickAction,person + ", who are you?"))                    

                # highthight html
                self.html_paragraph = self.html_paragraph.replace(
                    person, "<b><font color=\"red\">" + person + "</font></b>")
            for place in self.places_in_paragraph:
                print("[go to %s]" % place)
                print("[inspect %s]" % place)

                self.action_buttons.append(QtWidgets.QPushButton(self.groupBox))
                self.action_buttons[-1].setText("go to " + place)
                self.groupBoxGridLayout.addWidget(self.action_buttons[-1], (len(self.action_buttons)-1) // 3, (len(self.action_buttons)-1) % 3)
                self.action_buttons[-1].setToolTip("go to " + place)                    
                self.action_buttons[-1].clicked.connect(partial(self.clickAction, "go to " + place))                    

                self.action_buttons.append(QtWidgets.QPushButton(self.groupBox))
                self.action_buttons[-1].setText("inspect " + place)
                self.groupBoxGridLayout.addWidget(self.action_buttons[-1], (len(self.action_buttons)-1) // 3, (len(self.action_buttons)-1) % 3)
                self.action_buttons[-1].setToolTip("inspect " + place)                    
                self.action_buttons[-1].clicked.connect(partial(self.clickAction, "inspect " + place))                    

                self.html_paragraph = self.html_paragraph.replace(
                    place, "<b><font color=\"green\">" + place + "</font></b>")
            for event in self.events_in_paragraph:
                print("[think about %s]" % event)

                self.action_buttons.append(QtWidgets.QPushButton(self.groupBox))
                self.action_buttons[-1].setText("think about " + event)                    
                self.groupBoxGridLayout.addWidget(self.action_buttons[-1], (len(self.action_buttons)-1) // 3, (len(self.action_buttons)-1) % 3)
                self.action_buttons[-1].setToolTip("think about " + event)                    
                self.action_buttons[-1].clicked.connect(partial(self.clickAction, "think about " + event))                    

                self.html_paragraph = self.html_paragraph.replace(
                    event, "<b><font color=\"yellow\">" + event + "</font></b>")
            for item in self.items_in_paragraph:
                print("[take %s]" % item)
                print("[use %s]" % item)
                print("[push %s]" % item)

                self.action_buttons.append(QtWidgets.QPushButton(self.groupBox))
                self.action_buttons[-1].setText("take " + item)
                self.groupBoxGridLayout.addWidget(self.action_buttons[-1], (len(self.action_buttons)-1) // 3, (len(self.action_buttons)-1) % 3)
                self.action_buttons[-1].setToolTip("take " + person)                    
                self.action_buttons[-1].clicked.connect(partial(self.clickAction, "take " + item))                    

                self.action_buttons.append(QtWidgets.QPushButton(self.groupBox))
                self.action_buttons[-1].setText("use " + item)
                self.groupBoxGridLayout.addWidget(self.action_buttons[-1], (len(self.action_buttons)-1) // 3, (len(self.action_buttons)-1) % 3)
                self.action_buttons[-1].setToolTip("use " + person)                    
                self.action_buttons[-1].clicked.connect(partial(self.clickAction, "use " + item))                    

                self.action_buttons.append(QtWidgets.QPushButton(self.groupBox))
                self.action_buttons[-1].setText("push " + item)
                self.groupBoxGridLayout.addWidget(self.action_buttons[-1], (len(self.action_buttons)-1) // 3, (len(self.action_buttons)-1) % 3)
                self.action_buttons[-1].setToolTip("push " + person)                    
                self.action_buttons[-1].clicked.connect(partial(self.clickAction, "push " + item))                    

                self.html_paragraph = self.html_paragraph.replace(
                    item, "<b><font color=\"purple\">" + item + "</font></b>")

        # 6.2 Continue without taking an action 
        self.action_buttons.append(QtWidgets.QPushButton(self.groupBox))
        self.action_buttons[-1].setText("continue")
        self.groupBoxGridLayout.addWidget(self.action_buttons[-1], (len(self.action_buttons)-1) // 3, (len(self.action_buttons)-1) % 3)
        self.action_buttons[-1].setToolTip("continue")                    
        self.action_buttons[-1].clicked.connect(partial(self.clickAction, ""))

    def startNewGame(self):
        ui.textEdit.setHtml(
            self.html + "<b>Welcome to PCG adventures!</b>" + self.html_end)

        # 1. Enter name and story length [# of paragraphs]
        self.name = self.lineEdit.text()
        self.paragraphs = self.spinBox.value()

        # 2. Select setting [middle age, fantasy, horror]
        self.setting = self.comboBox.currentText()
        print("Setting %s" % self.setting)

        # 3. Load/generate introduction [Place, Time, Crew, Items]
        # -> place items in first place.
        #self.paragraph = random.choice(settings[self.setting].introductions)
        self.paragraph = settings["fantasy"].introductions[0]

        if self.paragraph_count < self.paragraphs:

            # Replace [name]
            self.paragraph = self.paragraph.replace("[name]", self.name)
            print(self.paragraph)

            self.extractEntities()

            self.html_paragraph = self.paragraph

            # 5.1 Clean up buttons

            self.createButtons()

            # append paragraph
            self.text = self.text + self.paragraph

            # highlight player name
            self.html_paragraph = self.html_paragraph.replace(self.name, "<b>" + self.name + "</b>")

            # append html and highlight
            self.html = self.html + self.html_paragraph
            ui.textEdit.setHtml(self.html + self.html_end)

            mylist = gpt2.generate(self.session, temperature=0.1,prefix=self.text, model_name="124M",length=100,return_as_list=True,nsamples=3,batch_size=3,top_p=0.99)
            for index, asd in enumerate(mylist):
                print("item " + str(index) + ": " + asd)

            # 7. Write twine paragraph including actions

            # 8. Wait for player input

            # 9. React to input and update meta data [add [place] to [known places], add [items], set [location], remove [item]]

            # 10. Truncate text

            # 11. Increase paragraph counter
            self.paragraph_count += 1

            # -> If end reached add text "So this is the end of our story."

            # 12. Generate following paragraph
            # If end is not reached -> Goto 4
        else:
            self.text = self.text + "The end"
            self.html = self.html + "<b>The end</b>"
            ui.textEdit.setHtml(self.html + self.html_end)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = InteractiveStoryUI()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
