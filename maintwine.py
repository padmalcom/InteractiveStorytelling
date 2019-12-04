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
        
    def getInventoryCode(self):
        return ["window.getInv = function() {return state.active.variables.inventory;}",
            "macros.initInv = {handler: function(place, macroName, params, parser) {state.active.variables.inventory = [];}};",
            "macros.addToInv = {handler: function(place, macroName, params, parser) {if (params.length == 0) {throwError(place, \"<<\" + macroName + \">>: no parameters given\");return;}    if (state.active.variables.inventory.indexOf(params[0]) == -1) {state.active.variables.inventory.push(params[0]);}}};",
            "macros.removeFromInv = {handler: function(place, macroName, params, parser) {if (params.length == 0) {throwError(place, \"<<\" + macroName + \">>: no parameters given\"); return;} var index = state.active.variables.inventory.indexOf(params[0]); if (index != -1) {state.active.variables.inventory.splice(index, 1);}}};",
            "macros.inv = {handler: function(place, macroName, params, parser) {if (state.active.variables.inventory.length == 0) {new Wikifier(place, 'nothing');} else {new Wikifier(place, state.active.variables.inventory.join(','));}}};",
            "macros.invWithLinks = {handler: function(place, macroName, params, parser) {if (state.active.variables.inventory.length == 0) {new Wikifier(place, 'nothing');} else {new Wikifier(place, '[[' + state.active.variables.inventory.join(']]<br>[[') + ']]');}}};",
            "macros.emptyInv = {handler: function(place, macroName, params, parser) {state.active.variables.inventory = []}};"]            

    def start(self):

        start_time = datetime.now()

        self.storyGenerator.reset()

        allSettings = list(self.storyGenerator.getSettings().keys())
        for s in allSettings:
            print("Setting:" + s)

        self.storyGenerator.setting = input("Select a setting: ")
        self.storyGenerator.name = input("Type your name: ")
        self.storyGenerator.party1 = input("Type a name of a party member: ")
        self.storyGenerator.party2 = input("Type the name of another member: ")
        self.storyGenerator.paragraphs = int(input("Enter a number of paragraphs: "))

        self.storyGenerator.setting_id = random.randrange(0, len(self.storyGenerator.getSettings()[self.storyGenerator.setting].introductions))
        self.storyGenerator.setting_id = 0 # temporary
        self.storyGenerator.paragraph = self.storyGenerator.getSettings()[self.storyGenerator.setting].introductions[self.storyGenerator.setting_id]

        # Open file to write
        f = open("C:/Users/admin/test.tw2", "w", encoding="utf-8")
        
        # Add inventory
        for line in self.getInventoryCode():
            f.write(line + "\n")
                    
        # Write start
        f.write("::StoryTitle\n")
        f.write("<<initInv>>")
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
        end_time = datetime.now()
        second_diff = (start_time - end_time).total_seconds()
        print("duration in seconds: " + second_diff.strftime("%d/%m/%Y %H:%M:%S"))


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
            paragraph = action["sentence"] + " " + end + " " + new_text
            self.storyGenerator.extractEntities(paragraph)
            html_paragraph = paragraph
            f.write(html_paragraph + "\n<b>THE END</b>\n")
            return
  
        # process given action
        if action["action"] == "take":
            inventory.append(action["entity"])
            f.write("<<addToInv \""+action["entity"]+"\">>")
        elif action["action"] == "use" and action["type"] == "item_from_inventory":
            if action["entity"] in inventory:
                inventory.remove(action["entity"])
                f.write("<<removeFromInv \""+action["entity"]+"\">>")
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
