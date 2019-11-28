from item import items
from combination import combinations
from functools import partial
import random
import os
from storygenerator import StoryGenerator
from collections import Counter, defaultdict
import sys

class TwineGenerator():
    def __init__(self):
        super().__init__()
        self.storyGenerator = StoryGenerator()
        self.action_buttons = []
        self.inventory_labels = []

    def reset(self):
        self.storyGenerator.reset()

    def start(self):

        self.storyGenerator.reset()

        allSettings = list(self.storyGenerator.getSettings().keys())
        for s in allSettings:
            print("Setting:" + s)

        self.storyGenerator.setting = input("Select a setting")
        self.storyGenerator.name = input("Type your name")
        self.storyGenerator.paragraphs = int(intput("Enter a number of paragraphs"))

        self.storyGenerator.setting_id = random.randrange(0, len(self.storyGenerator.getSettings()[self.storyGenerator.setting].introductions))
        self.storyGenerator.setting_id = 0 # temporary
        self.storyGenerator.paragraph = self.storyGenerator.getSettings()[self.storyGenerator.setting].introductions[self.storyGenerator.setting_id]

        # Write intro
        f = open(p"C:\Users\admin\test.tw", "w")
        f.write("::StoryTitle")
        f.write("A " + self.storyGenerator.setting + " story")
        f.writelines(["", "::Configuration [twee2]","Twee2::build_config.story_ifid = '7870917a-11c5-4bb8-a945-c810834c8229'","Twee2::build_config.story_format = 'SugarCube2'", ""])

        # Write start
        self.storyGenerator.extractEntities(self.storyGenerator.paragraph)
        self.storyGenerator.html_paragraph = self.storyGenerator.paragraph
        self.storyGenerator.html_paragraph = self.storyGenerator.highlightEntities(self.storyGenerator.html_paragraph)
        self.storyGenerator.html_paragraph = self.storyGenerator.html_paragraph.replace(self.storyGenerator.name, "<b>" + self.storyGenerator.name + "</b>")

        self.recursivelyContinue(f, self.storyGenerator.paragraph, self.storyGenerator.html_paragraph, self.storyGenerator.inventory, "1", 0, "", "", "")

        self.storyGenerator.generateEnd()

    def recursivelyContinue(self, file, text, html, inventory, twineid, depth, action, entity, action_sentence):

        # end reached?
        if (depth == self.storyGenerator.paragraps-1):
            return

        # generate twine paragraph id
        if twineid == 1:
            f.write("::Start")
        else:
            f.write("::" + str(twineid))
  
        # write text
        f.write(html)

        # process given action
        if action["action"] == "take":
            inventory.append(entity)
        elif action["action"] == "use from inventory":
            inventory.remove(entity)

        # generate next paragraph
        self.storyGenerator.text = text
        trucated_text = self.storyGenerator.truncateLastSentences(200)
        new_text = self.storyGenerator.generateText(trucated_text)
        paragraph = action_sentence + " " + new_text

        # extract entities
        self.storyGenerator.extractEntities(paragraph)

        html_paragraph = paragraph

        f.write(html_paragraph)

        # Generate links
        actions = self.storyGenerator.generateActions()
        for idx, action in enumerate(actions):
            f.write("[[" + action["short"] + "->" + str(twineid) + "_" + str(idx)]]")

            # call recursive generation
            self.recursivelyContinue(file, text + paragraph, html + html_paragraph, inventory, str(twineid) + "_" + str(idx), action["action"], action["entity"], action["sentence"])


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
                self.action_buttons[-1].setText(action["simple"])

        # 6.2 Continue without taking an action 
        self.action_buttons.append(QtWidgets.QPushButton(self.groupBox))
        self.action_buttons[-1].setText("continue")
        self.groupBoxGridLayout.addWidget(self.action_buttons[-1], (len(self.action_buttons)-1) // 3, (len(self.action_buttons)-1) % 3)
        self.action_buttons[-1].setToolTip("continue")
        self.action_buttons[-1].clicked.connect(partial(self.clickAction, "", ""))

   


if __name__ == '__main__':
    tg = TwineGenerator()
