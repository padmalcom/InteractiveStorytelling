from item import items
from combination import combinations
from functools import partial
import random
import os
from storygenerator import StoryGenerator
from collections import Counter, defaultdict

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

        allSettings = list(self.storyGenerator.getSettings().keys())
        for s in allSettings:
            self.comboBox.addItem(_translate("Dialog", s))
        self.label_3.setText(_translate("Dialog", "Player name:"))
        self.pushButton_2.setText(_translate("Dialog", "Start game"))
        self.label_2.setText(_translate("Dialog", "Paragraphs:"))
        self.pushButton.setText(_translate("Dialog", "Quit"))
        self.textEdit.setHtml(_translate("Dialog", self.storyGenerator.html + self.storyGenerator.HTML_END))
        self.groupBox.setTitle(_translate("Dialog", "Actions"))
        self.groupBox_2.setTitle(_translate("Dialog", "Inventory"))
        self.lineEdit.setText(_translate("Dialog", "Jim"))
        self.spinBox.setValue(self.storyGenerator.paragraphs)

    def __init__(self):
        super().__init__()
        self.storyGenerator = StoryGenerator()
        self.action_buttons = []
        self.inventory_labels = []

    def reset(self):
        self.storyGenerator.reset()
        for button in self.action_buttons:
            self.groupBoxGridLayout.removeWidget(button)
            button.deleteLater()
            button = None
        self.action_buttons.clear()
        for label in self.inventory_labels:
            self.groupBox_2GridLayout.removeWidget(label)
            label.deleteLater()
            button = None
        self.inventory_labels.clear()

    def clickAction(self, action, entity, action_sentence):

        # If no action is defined, just continue on the last text block.
        #if (action == "" and entity == ""):
        #    action_sentence = ""
        #else:
            # Select action template
        #    action_sentence = self.storyGenerator.getActionTemplates(action, entity)

        # add to inventory
        if action == "take": # and not entity in self.storyGenerator.inventory
            # todo: check if take was a success
            self.storyGenerator.inventory.append(entity)
            self.inventory_labels.append(QtWidgets.QLabel(self.groupBox_2))
            self.inventory_labels[-1].setText(entity)
            self.groupBox_2GridLayout.addWidget(self.inventory_labels[-1], (len(self.inventory_labels)-1) // 3, (len(self.inventory_labels)-1) % 3)
        elif action == "use from inventory":
            self.storyGenerator.inventory.remove(entity)
            # delete label
            for label in self.inventory_labels:
                if label.text == entity:
                    self.groupBox_2GridLayout.removeWidget(label)
                    label.deleteLater()
                    self.inventory_labels.remove(label)
                    break
                    #label = None

        self.storyGenerator.text = self.storyGenerator.text + " " + action_sentence

        # Create an end
        if self.storyGenerator.current_paragraphs >= self.storyGenerator.paragraphs:
            end = self.storyGenerator.generateEnd()
            self.storyGenerator.text = self.storyGenerator.text + " " + action_sentence + " " + end

            trucated_text = self.storyGenerator.truncateLastSentences(200)
            new_text = self.storyGenerator.generateText(trucated_text)

            self.storyGenerator.paragraph = new_text

            # extract entities
            self.storyGenerator.extractEntities(self.storyGenerator.paragraph)

            self.storyGenerator.html_paragraph = self.storyGenerator.paragraph
            
            self.storyGenerator.html_paragraph = self.storyGenerator.highlightEntities(self.storyGenerator.html_paragraph)
            self.storyGenerator.html_paragraph = self.storyGenerator.html_paragraph.replace(self.storyGenerator.name, "<b>" + self.storyGenerator.name + "</b>")

            # append html and text
            self.storyGenerator.text = self.storyGenerator.text + self.storyGenerator.paragraph
            temp_html = self.storyGenerator.html + " <span style=\"background-color: #FFFF00\">" + self.storyGenerator.html_paragraph + "</span>"
            self.storyGenerator.html = self.storyGenerator.html + " " + self.storyGenerator.html_paragraph
            ui.textEdit.setHtml(temp_html + "<br><b>THE END</b>" + self.storyGenerator.HTML_END)
            
        # Create a normal paragraph
        else:
            # generate next paragraph
            trucated_text = self.storyGenerator.truncateLastSentences(200)
            new_text = self.storyGenerator.generateText(trucated_text)
            self.storyGenerator.paragraph = action_sentence + " " + new_text

            # extract entities
            self.storyGenerator.extractEntities(self.storyGenerator.paragraph)

            self.storyGenerator.html_paragraph = self.storyGenerator.paragraph

            # 5.1 Clean up buttons
            self.createButtons()

            # highlight player name
            self.storyGenerator.html_paragraph = self.storyGenerator.highlightEntities(self.storyGenerator.html_paragraph)
            self.storyGenerator.html_paragraph = self.storyGenerator.html_paragraph.replace(self.storyGenerator.name, "<b>" + self.storyGenerator.name + "</b>")

            # append html and text
            self.storyGenerator.text = self.storyGenerator.text + " " + self.storyGenerator.paragraph
            temp_html = self.storyGenerator.html + " <span style=\"background-color: #FFFF00\">" + self.storyGenerator.html_paragraph + "</span>"
            self.storyGenerator.html = self.storyGenerator.html + " " + self.storyGenerator.html_paragraph
            ui.textEdit.setHtml(temp_html + self.storyGenerator.HTML_END)

            self.storyGenerator.current_paragraphs +=1

    def createButtons(self):

        # 5.2 Are there any buttons? Destroy
        for button in self.action_buttons:
            self.groupBoxGridLayout.removeWidget(button)
            button.deleteLater()
            button = None
        self.action_buttons.clear()

        actions = self.storyGenerator.generateActions()

        for action in actions:
            # 6.2 Continue without taking an action 
            print(action)
            self.action_buttons.append(QtWidgets.QPushButton(self.groupBox))
            self.action_buttons[-1].setText(action["action"] + " " + action["entity"])
            self.groupBoxGridLayout.addWidget(self.action_buttons[-1], (len(self.action_buttons)-1) // 3, (len(self.action_buttons)-1) % 3)
            self.action_buttons[-1].setToolTip(action["sentence"])
            self.action_buttons[-1].clicked.connect(partial(self.clickAction, action["action"], action["entity"], action["sentence"]))

            if (action["type"] == "item_from_inventory"):
                self.action_buttons[-1].setStyleSheet("background-color: yellow")

            if (action["type"] == "combination"):
                self.action_buttons[-1].setStyleSheet("background-color: green")

        # 5.3 Check if there are any actions
        """if (len(self.storyGenerator.people_in_paragraph) > 0 or len(self.storyGenerator.places_in_paragraph) > 0 or
            len(self.storyGenerator.events_in_paragraph) > 0 or len(self.storyGenerator.items_in_paragraph) > 0 or
            (len(self.storyGenerator.nouns_in_paragraph) > 0 and self.storyGenerator.USE_NOUNS)):

            # 6. Generate actions [Talk to, Take [item] {based on nlp}, go to [Place], Inspect [Item, Place, Person, Item in inventory], Push, Pull {fun?},
            # insult/compliment [Person], use [item], combine [item, item]]
            action_count = 0
            for person in self.storyGenerator.people_in_paragraph:
                actions = ["compliment", "insult", "look at", "who are you,"]
                for action in actions:
                    if self.storyGenerator.MAX_ACTIONS > -1 and action_count == self.storyGenerator.MAX_ACTIONS-1:
                        break
                    else:
                        self.action_buttons.append(QtWidgets.QPushButton(self.groupBox))
                        self.action_buttons[-1].setText(action + " " + person)
                        self.groupBoxGridLayout.addWidget(self.action_buttons[-1], (len(self.action_buttons)-1) // 3, (len(self.action_buttons)-1) % 3)
                        self.action_buttons[-1].setToolTip(action + " " + person)                    
                        self.action_buttons[-1].clicked.connect(partial(self.clickAction, action, person))
                        action_count +=1

            for place in self.storyGenerator.places_in_paragraph:
                actions = ["go to", "look at"]
                for action in actions:
                    if self.storyGenerator.MAX_ACTIONS > -1 and action_count == self.storyGenerator.MAX_ACTIONS-1:
                        break
                    else:                    
                        self.action_buttons.append(QtWidgets.QPushButton(self.groupBox))
                        self.action_buttons[-1].setText(action + " " + place)
                        self.groupBoxGridLayout.addWidget(self.action_buttons[-1], (len(self.action_buttons)-1) // 3, (len(self.action_buttons)-1) % 3)
                        self.action_buttons[-1].setToolTip(action + " " + place)                    
                        self.action_buttons[-1].clicked.connect(partial(self.clickAction, action, place))
                        action_count +=1

            for event in self.storyGenerator.events_in_paragraph:
                actions = ["think about"]
                for action in actions:
                    if self.storyGenerator.MAX_ACTIONS > -1 and action_count == self.storyGenerator.MAX_ACTIONS-1:
                        break
                    else:
                        self.action_buttons.append(QtWidgets.QPushButton(self.groupBox))
                        self.action_buttons[-1].setText(action + " " + event)
                        self.groupBoxGridLayout.addWidget(self.action_buttons[-1], (len(self.action_buttons)-1) // 3, (len(self.action_buttons)-1) % 3)
                        self.action_buttons[-1].setToolTip(action + " " + event)                    
                        self.action_buttons[-1].clicked.connect(partial(self.clickAction, action, event))
                        action_count +=1

            for item in self.storyGenerator.items_in_paragraph:
                actions = ["take", "use", "push"]
                for action in actions:
                    if self.storyGenerator.MAX_ACTIONS > -1 and action_count == self.storyGenerator.MAX_ACTIONS-1:
                        break
                    else:
                        self.action_buttons.append(QtWidgets.QPushButton(self.groupBox))
                        self.action_buttons[-1].setText(action + " " + item)
                        self.groupBoxGridLayout.addWidget(self.action_buttons[-1], (len(self.action_buttons)-1) // 3, (len(self.action_buttons)-1) % 3)
                        self.action_buttons[-1].setToolTip(action + " " + item)
                        self.action_buttons[-1].clicked.connect(partial(self.clickAction, action, item))
                        action_count +=1

            for item in self.storyGenerator.inventory:
                if self.storyGenerator.MAX_ACTIONS > -1 and action_count == self.storyGenerator.MAX_ACTIONS-1:
                    break
                else:
                    self.action_buttons.append(QtWidgets.QPushButton(self.groupBox))
                    self.action_buttons[-1].setText("use " + item + " from inventory")
                    self.groupBoxGridLayout.addWidget(self.action_buttons[-1], (len(self.action_buttons)-1) // 3, (len(self.action_buttons)-1) % 3)
                    self.action_buttons[-1].setToolTip("use " + item + " from inventory")
                    self.action_buttons[-1].clicked.connect(partial(self.clickAction, "use from inventory", item))
                    action_count +=1

            if (self.storyGenerator.USE_NOUNS):
                for noun in self.storyGenerator.nouns_in_paragraph:
                    actions = ["take", "use", "push", "pull", "open", "close", "look at", "talk to"]
                    for action in actions:
                        if self.storyGenerator.MAX_ACTIONS > -1 and action_count == self.storyGenerator.MAX_ACTIONS-1:
                            break
                        else:
                            self.action_buttons.append(QtWidgets.QPushButton(self.groupBox))
                            self.action_buttons[-1].setText(action + " " + noun)
                            self.groupBoxGridLayout.addWidget(self.action_buttons[-1], (len(self.action_buttons)-1) // 3, (len(self.action_buttons)-1) % 3)
                            self.action_buttons[-1].setToolTip(action + " " + noun)                    
                            self.action_buttons[-1].clicked.connect(partial(self.clickAction, action, noun))
                            action_count +=1"""


        # 6.2 Continue without taking an action 
        self.action_buttons.append(QtWidgets.QPushButton(self.groupBox))
        self.action_buttons[-1].setText("continue")
        self.groupBoxGridLayout.addWidget(self.action_buttons[-1], (len(self.action_buttons)-1) // 3, (len(self.action_buttons)-1) % 3)
        self.action_buttons[-1].setToolTip("continue")
        self.action_buttons[-1].clicked.connect(partial(self.clickAction, "", ""))

    def startNewGame(self):
        self.storyGenerator.html = ""
        self.storyGenerator.html_paragraph = ""
        self.storyGenerator.paragraph = ""
        self.storyGenerator.current_paragraphs = 0
        self.storyGenerator.people_in_paragraph.clear()
        self.storyGenerator.places_in_paragraph.clear()
        self.storyGenerator.events_in_paragraph.clear()
        self.storyGenerator.items_in_paragraph.clear()
        self.storyGenerator.nouns_in_paragraph.clear()

        ui.textEdit.setHtml(
            self.storyGenerator.html + "<b>Welcome to PCG adventures!</b>" + self.storyGenerator.HTML_END)

        # 1. Enter name and story length [# of paragraphs]
        self.storyGenerator.name = self.lineEdit.text()
        self.storyGenerator.paragraphs = self.spinBox.value()

        # 2. Select setting [middle age, fantasy, horror]
        self.storyGenerator.setting = self.comboBox.currentText()

        # 3. Load/generate introduction [Place, Time, Crew, Items]
        # -> place items in first place.
        self.storyGenerator.setting_id = random.randrange(0, len(self.storyGenerator.getSettings()[self.storyGenerator.setting].introductions))
        self.storyGenerator.setting_id = 0 # temporary
        self.storyGenerator.paragraph = self.storyGenerator.getSettings()[self.storyGenerator.setting].introductions[self.storyGenerator.setting_id]

        if self.storyGenerator.current_paragraphs < self.storyGenerator.paragraphs:

            # Replace [name]
            self.storyGenerator.paragraph = self.storyGenerator.paragraph.replace("[name]", self.storyGenerator.name)

            self.storyGenerator.extractEntities(self.storyGenerator.paragraph)

            # temporary element to be appended to html and text
            self.storyGenerator.html_paragraph = self.storyGenerator.paragraph

            # 5.1 Clean up buttons and create new
            self.createButtons()

            # Highlight entities
            self.storyGenerator.html_paragraph = self.storyGenerator.highlightEntities(self.storyGenerator.html_paragraph)

            # append paragraph
            self.storyGenerator.text = self.storyGenerator.text + " " + self.storyGenerator.paragraph

            # highlight player name
            self.storyGenerator.html_paragraph = self.storyGenerator.html_paragraph.replace(self.storyGenerator.name, "<b>" + self.storyGenerator.name + "</b>")

            # append html and highlight
            temp_html = self.storyGenerator.html + " <span style=\"background-color: #FFFF00\">" + self.storyGenerator.html_paragraph + "</span>"
            self.storyGenerator.html = self.storyGenerator.html + " " + self.storyGenerator.html_paragraph
            ui.textEdit.setHtml(temp_html + self.storyGenerator.HTML_END)

            # 11. Increase paragraph counter
            self.storyGenerator.current_paragraphs += 1

        else:
            self.storyGenerator.generateEnd()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = InteractiveStoryUI()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
