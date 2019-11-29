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

        self.EMPTY_ACTION = {"type":"", "action":"", "entity":"", "sentence":"", "simple": "", "probability":""}

    def reset(self):
        self.storyGenerator.reset()

    def start(self):

        self.storyGenerator.reset()

        allSettings = list(self.storyGenerator.getSettings().keys())
        for s in allSettings:
            print("Setting:" + s)

        self.storyGenerator.setting = input("Select a setting: ")
        self.storyGenerator.name = input("Type your name: ")
        self.storyGenerator.paragraphs = int(input("Enter a number of paragraphs: "))

        self.storyGenerator.setting_id = random.randrange(0, len(self.storyGenerator.getSettings()[self.storyGenerator.setting].introductions))
        self.storyGenerator.setting_id = 0 # temporary
        self.storyGenerator.paragraph = self.storyGenerator.getSettings()[self.storyGenerator.setting].introductions[self.storyGenerator.setting_id]

        # Write intro
        f = open("C:/Users/admin/test.tw", "w")
        f.write("::StoryTitle\r\n")
        f.write("A " + self.storyGenerator.setting + " story\r\n")
        f.writelines(["\r\n", "::Configuration [twee2]\r\n","Twee2::build_config.story_ifid = '7870917a-11c5-4bb8-a945-c810834c8229'\r\n","Twee2::build_config.story_format = 'SugarCube2'\r\n", "\r\n"])

        # Write start
        self.storyGenerator.extractEntities(self.storyGenerator.paragraph)
        self.storyGenerator.html_paragraph = self.storyGenerator.paragraph
        self.storyGenerator.html_paragraph = self.storyGenerator.highlightEntities(self.storyGenerator.html_paragraph)
        self.storyGenerator.html_paragraph = self.storyGenerator.html_paragraph.replace(self.storyGenerator.name, "<b>" + self.storyGenerator.name + "</b>")

        self.recursivelyContinue(f, self.storyGenerator.paragraph, self.storyGenerator.html_paragraph, self.storyGenerator.inventory, "1", 0, self.EMPTY_ACTION)

        #self.storyGenerator.generateEnd()
        f.write("The end\r\n")
        f.close()

    def recursivelyContinue(self, f, text, html, inventory, twineid, depth, action):

        # end reached?
        if (depth == self.storyGenerator.paragraphs-1):
            return

        # generate twine paragraph id
        if twineid == 1:
            f.write("::Start\r\n")
        else:
            f.write("::" + str(twineid) + "\r\n")
  
        # write text
        f.write(html)

        # process given action
        if action["action"] == "take":
            inventory.append(action["entity"])
        elif action["action"] == "use" and action["type"] == "item_from_inventory":
            inventory.remove(action["entity"])

        # generate next paragraph
        self.storyGenerator.text = text
        trucated_text = self.storyGenerator.truncateLastSentences(200)
        new_text = self.storyGenerator.generateText(trucated_text)
        paragraph = action["sentence"] + " " + new_text

        # extract entities
        self.storyGenerator.extractEntities(paragraph)

        html_paragraph = paragraph

        f.write(html_paragraph)

        # Generate links
        actions = self.storyGenerator.generateActions()
        for idx, action in enumerate(actions):
            f.write("[[" + action["simple"] + "->" + str(twineid) + "_" + str(idx) +"]]\r\n")

            # call recursive generation
            self.recursivelyContinue(f, text + paragraph, html + html_paragraph, inventory, str(twineid) + "_" + str(idx), depth, action)

        # simple continue button
        f.write("[[continue->" + len(actions)+"]]\r\n")
        self.recursivelyContinue(f, text + paragraph, html + html_paragraph, inventory, str(twineid) + "_" + str(idx), depth, self.EMPTY_ACTION)

if __name__ == '__main__':
    tg = TwineGenerator()
    tg.start()
