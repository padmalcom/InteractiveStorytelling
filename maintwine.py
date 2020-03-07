from item import items
from combination import combinations
from functools import partial
import random
import os
from storygenerator import StoryGenerator
from collections import Counter, defaultdict
import sys
from datetime import datetime
import matplotlib.pyplot as plt

class TwineGenerator():
    def __init__(self):
        super().__init__()
        self.storyGenerator = StoryGenerator()
        self.action_buttons = []
        self.inventory_labels = []
        self.out_path = ""

        self.EMPTY_ACTION = {"type":"", "action":"", "entity":"", "sentence":"", "simple": "", "probability":""}

        print("Initialization done.")

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

        all_paragraphs = []
        paragraph_coherences = []

        inventory = []

        # Where is the story stored?
        self.out_path = r"C:/Users/admin/" + datetime.now().strftime("story_%d.%m.%Y_%H-%M-%S")+ "_para" + str(self.storyGenerator.paragraphs)
        if os.path.exists(self.out_path):
            print("Story directory already exists. Exiting")
        else:
            os.mkdir(self.out_path)
        
        # do not use self.storyGenerator.paragraph since we are in a tree structure
        paragraph = self.storyGenerator.getSettings()[self.storyGenerator.setting].introductions[self.storyGenerator.setting_id]

        paragraph = paragraph.replace("[name]", self.storyGenerator.name)
        all_paragraphs.append(paragraph)
        coh = self.storyGenerator.calculateParagraphCoherence(all_paragraphs)
        paragraph_coherences.append(coh)
        print("Coherence is: " + str(coh))

        # Plot coherence graph
        fig, ax = plt.subplots(nrows=1, ncols=1)
        fig.set_size_inches(4.0, 3.0)
        ax.plot(range(0,len(paragraph_coherences)), paragraph_coherences)
        ax.set_xlabel("Paragraph")
        ax.set_ylabel("Coherence")
        fig.savefig(self.out_path + r"/plt" + str(len(paragraph_coherences)) + ".png")
        plt.close(fig)

        # Open file to write
        absolute_path = self.out_path + r"/story.tw2"
        f = open(absolute_path, "w", encoding="utf-8")
        
        # Add inventory
        for line in self.getInventoryCode():
            f.write(line + "\n")
                    
        # Write start
        f.write("::StoryTitle\n")

        f.write("A " + self.storyGenerator.setting + " story\n")
        f.writelines(["\n", "::Configuration [twee2]\n","Twee2::build_config.story_ifid = '7870917a-11c5-4bb8-a945-c810834c8229'\n","Twee2::build_config.story_format = 'SugarCube2'\n", "\n"])


        # Write start
        self.storyGenerator.extractEntities(paragraph)
        html_paragraph = paragraph
        html_paragraph = self.storyGenerator.highlightEntities(html_paragraph)
        html_paragraph = html_paragraph.replace(self.storyGenerator.name, "<b>" + self.storyGenerator.name + "</b>")
        
        self.recursivelyContinue(f, paragraph, html_paragraph, inventory, "1", 0, self.EMPTY_ACTION, all_paragraphs, paragraph_coherences)

        f.write("The end\n")
        f.close()
        end_time = datetime.now()
        second_diff = (end_time - start_time).total_seconds()
        print("Started at " + str(start_time) + ", ended at " + str(end_time) + ", duration in seconds: " + str(second_diff))
        os.rename(self.out_path, self.out_path + "_done_in_" + str(second_diff))


    def recursivelyContinue(self, f, text, html, inventory, twineid, depth, action, all_paragraphs, paragraph_coherences):

        print("Depth " + str(depth) + " of " + str(self.storyGenerator.paragraphs))

        # generate twine paragraph id
        if twineid == "1":
            f.write("::Start\n")
            f.write("<<initInv>>")
            f.write(html)
        else:
            f.write("::" + str(twineid) + "\n")

        # end reached?
        if (depth == self.storyGenerator.paragraphs):
            end = self.storyGenerator.generateEnd()
            text = text + " " + action["sentence"] + " " + end
            truncated_text = self.storyGenerator.truncateLastSentences(text, self.storyGenerator.TRUCATED_LAST_TEXT)
            try:
                new_text = self.storyGenerator.generateText(truncated_text)
            except:
                print("0 Generation error on truncated_text: '" + truncated_text + "'")
                new_text = ""
            paragraph = action["sentence"] + " " + end + " " + new_text
            
            # coherence
            all_paragraphs.append(new_text)
            coh = self.storyGenerator.calculateParagraphCoherence(all_paragraphs)
            paragraph_coherences.append(coh)
            print("Coherence is: " + str(coh))

            # Plot coherence graph
            fig, ax = plt.subplots(nrows=1, ncols=1)
            fig.set_size_inches(4.0, 3.0)
            ax.plot(range(0,len(paragraph_coherences)), paragraph_coherences)
            ax.set_xlabel("Paragraph")
            ax.set_ylabel("Coherence")
            fig.savefig(self.out_path + r"/plt" + str(twineid) + ".png")
            plt.close(fig)

            self.storyGenerator.extractEntities(paragraph)
            html_paragraph = paragraph

            # highlight entities and names
            html_paragraph = self.storyGenerator.highlightEntities(html_paragraph)
            html_paragraph = html_paragraph.replace(self.storyGenerator.name, "<b>" + self.storyGenerator.name + "</b>")

            # finally append entire text
            text = text + " " + paragraph
            html = html + " " + html_paragraph

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
        text = text + " " + action["sentence"]
        truncated_text = self.storyGenerator.truncateLastSentences(text, self.storyGenerator.TRUCATED_LAST_TEXT)
        try:
            new_text = self.storyGenerator.generateText(truncated_text)
        except:
            print("1 Generation error on truncated_text: '" + truncated_text + "'")
            new_text = ""

        #paragraph = action["sentence"] + " " + new_text
        paragraph = action["sentence"] + " " +new_text

        all_paragraphs.append(new_text)
        coh = self.storyGenerator.calculateParagraphCoherence(all_paragraphs)
        paragraph_coherences.append(coh)
        print("Coherence is: " + str(coh))

        # Plot coherence graph
        fig, ax = plt.subplots(nrows=1, ncols=1)
        fig.set_size_inches(4.0, 3.0)
        ax.plot(range(0,len(paragraph_coherences)), paragraph_coherences)
        ax.set_xlabel("Paragraph")
        ax.set_ylabel("Coherence")
        image_path = self.out_path + r"/plt" + str(twineid) + ".png"
        fig.savefig(image_path)
        plt.close(fig)  

        # extract entities
        self.storyGenerator.extractEntities(paragraph)

        html_paragraph = paragraph

        f.write(html_paragraph + "\n<img src=\"plt" + str(twineid) + ".png\"><br>")

        # Generate links
        actions = self.storyGenerator.generateActions()
        for idx, action in enumerate(actions):
            f.write("[[" + action["simple"] + "->" + twineid + "_" + str(idx) +"]]\n")

        # simple continue button
        f.write("[[continue->" + twineid + "_" + str(len(actions))+"]]\n\n")
        for idx, action in enumerate(actions):
            # generate target for each action
            self.recursivelyContinue(f, text + paragraph, html + html_paragraph, inventory, twineid + "_" + str(idx), depth+1, action, all_paragraphs.copy(), paragraph_coherences.copy())

        # generate continue paragraph
        self.recursivelyContinue(f, text + paragraph, html + html_paragraph, inventory, twineid + "_" + str(len(actions)), depth+1, self.EMPTY_ACTION, all_paragraphs.copy(), paragraph_coherences.copy())

if __name__ == '__main__':
    tg = TwineGenerator()
    tg.start()
