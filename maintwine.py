from item import items
from combination import combinations
from functools import partial
import random
import os
from storygenerator import StoryGenerator
from collections import Counter, defaultdict
import sys
from datetime import datetime

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

        start_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

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
        f = open("C:/Users/admin/test.tw2", "w", encoding="utf-8")
        f.write("::StoryTitle\n")
        f.write("A " + self.storyGenerator.setting + " story\n")
        f.writelines(["\n", "::Configuration [twee2]\n","Twee2::build_config.story_ifid = '7870917a-11c5-4bb8-a945-c810834c8229'\n","Twee2::build_config.story_format = 'SugarCube2'\n", "\n"])

        # Write start
        self.storyGenerator.extractEntities(self.storyGenerator.paragraph)
        self.storyGenerator.html_paragraph = self.storyGenerator.paragraph
        self.storyGenerator.html_paragraph = self.storyGenerator.highlightEntities(self.storyGenerator.html_paragraph)
        self.storyGenerator.html_paragraph = self.storyGenerator.html_paragraph.replace(self.storyGenerator.name, "<b>" + self.storyGenerator.name + "</b>")

        self.recursivelyContinue(f, self.storyGenerator.paragraph, self.storyGenerator.html_paragraph, self.storyGenerator.inventory, "1", 0, self.EMPTY_ACTION)


        f.write("The end\n")
        f.close()
        end_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        second_diff = (start_time - end_time).total_seconds()
        print("duration in seconds: " + str(second_diff))


    def recursivelyContinue(self, f, text, html, inventory, twineid, depth, action):

        print("Depth " + str(depth) + " of " + str(self.storyGenerator.paragraphs-1))

        # generate twine paragraph id
        if twineid == "1":
            f.write("::Start\n")
            f.write(html)
        else:
            f.write("::" + str(twineid) + "\n")

        # end reached?
        if (depth == self.storyGenerator.paragraphs):
            end = self.storyGenerator.generateEnd()
            self.storyGenerator.text = self.storyGenerator.text + " " + action["sentence"] + " " + end
            trucated_text = self.storyGenerator.truncateLastSentences(200)
            new_text = self.storyGenerator.generateText(trucated_text)
            paragraph = action["sentence"] + " " +new_text
            self.storyGenerator.extractEntities(paragraph)
            html_paragraph = paragraph
            f.write(html_paragraph + "\n<b>THE END</b>\n")
            return
  
        # process given action
        if action["action"] == "take":
            inventory.append(action["entity"])
        elif action["action"] == "use" and action["type"] == "item_from_inventory":
            if action["entity"] in inventory:
                inventory.remove(action["entity"])
            else:
                print("Trying to remove " + action["entity"] + " but not in inv.")

        # generate next paragraph
        #self.storyGenerator.text = text
        self.storyGenerator.text = text + action["sentence"]
        trucated_text = self.storyGenerator.truncateLastSentences(200)
        new_text = self.storyGenerator.generateText(trucated_text)
        #paragraph = action["sentence"] + " " + new_text
        paragraph = action["sentence"] + " " +new_text

        # extract entities
        self.storyGenerator.extractEntities(paragraph)

        html_paragraph = paragraph

        f.write(html_paragraph + "\n")

        # Generate links
        actions = self.storyGenerator.generateActions()
        for idx, action in enumerate(actions):
            f.write("[[" + action["simple"] + "->" + twineid + "_" + str(idx) +"]]\n")

        # simple continue button
        f.write("[[continue->" + twineid + "_" + str(len(actions))+"]]\n\n")
        for idx, action in enumerate(actions):
            # generate target for each action
            self.recursivelyContinue(f, text + paragraph, html + html_paragraph, inventory, twineid + "_" + str(idx), depth+1, action)

        # generate continue paragraph
        self.recursivelyContinue(f, text + paragraph, html + html_paragraph, inventory, twineid + "_" + str(len(actions)), depth+1, self.EMPTY_ACTION)

if __name__ == '__main__':
    tg = TwineGenerator()
    tg.start()
