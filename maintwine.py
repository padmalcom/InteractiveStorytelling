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
from sentiment import Sentiment

class TwineGenerator():
    def __init__(self):
        super().__init__()
        self.storyGenerator = StoryGenerator()
        self.action_buttons = []
        self.inventory_labels = []
        self.out_path = ""

        self.total_nodes = 0
        self.current_node = 0

        self.EMPTY_ACTION = {"type":"", "action":"", "entity":"", "sentence":"", "simple": "", "probability":""}

        self.BERT_ACTIONS = True

        self.sentiment = Sentiment()

        print("Initialization done.")

    def reset(self):
        self.storyGenerator.reset()
        
    def getInventoryCode(self):
        return ["::MacroPassage[script]",
            "window.getInv = function() {return state.active.variables.inventory;}",
            "macros.initInv = {handler: function(place, macroName, params, parser) {state.active.variables.inventory = [];}};",
            "macros.addToInv = {handler: function(place, macroName, params, parser) {if (params.length == 0) {throwError(place, \"<<\" + macroName + \">>: no parameters given\");return;}    if (state.active.variables.inventory.indexOf(params[0]) == -1) {state.active.variables.inventory.push(params[0]);}}};",
            "macros.removeFromInv = {handler: function(place, macroName, params, parser) {if (params.length == 0) {throwError(place, \"<<\" + macroName + \">>: no parameters given\"); return;} var index = state.active.variables.inventory.indexOf(params[0]); if (index != -1) {state.active.variables.inventory.splice(index, 1);}}};",
            "macros.inv = {handler: function(place, macroName, params, parser) {if (state.active.variables.inventory.length == 0) {new Wikifier(place, 'nothing');} else {new Wikifier(place, state.active.variables.inventory.join(','));}}};",
            "macros.invWithLinks = {handler: function(place, macroName, params, parser) {if (state.active.variables.inventory.length == 0) {new Wikifier(place, 'nothing');} else {new Wikifier(place, '[[' + state.active.variables.inventory.join(']]<br>[[') + ']]');}}};",
            "macros.emptyInv = {handler: function(place, macroName, params, parser) {state.active.variables.inventory = []}};",
            "",
            "::StoryCaption",
            "<<invWithLinks>>",
            ""]            

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
        self.storyGenerator.MAX_ACTIONS = int(input("Enter the number of actions in a paragraph: "))
        self.addContinueButton = int(input("Offer a continue button (1 yes, 0 no): "))

        if (self.addContinueButton != 0 and self.addContinueButton != 1):
            self.addContinueButton = 0
            print("Continue button was disabled due to an invalid input.")

        self.storyGenerator.setting_id = random.randrange(0, len(self.storyGenerator.getSettings()[self.storyGenerator.setting].introductions))
        self.storyGenerator.setting_id = 0 # temporary

        all_paragraphs = []
        paragraph_coherences = []
        paragraph_sentiments = []
        paragraph_topics = []

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
        paragraph_coherences.append(coh[0])
        paragraph_topics.append(coh[1][len(coh[1])-1])
        print("Coherence is: " + str(coh[0]))
        print("Topics are: " + str(coh[1][len(coh[1])-1]))

        sentiment = self.sentiment.sentiment(paragraph)
        paragraph_sentiments.append(sentiment)
        print("Sentiment is: " + str(sentiment))

        # Plot coherence graph
        fig, ax = plt.subplots(nrows=1, ncols=1)
        ax.plot(range(0,len(paragraph_coherences)), paragraph_coherences)
        ax.set_xlabel("Paragraph")
        ax.set_ylabel("Coherence")
        fig.savefig(self.out_path + r"/coh_" + str(len(paragraph_coherences)) + ".png")
        plt.close(fig)

        # Plot sentiment graph
        fig, ax = plt.subplots(nrows=1, ncols=1)
        ax.plot(range(0,len(paragraph_sentiments)), paragraph_sentiments)
        ax.set_xlabel("Paragraph")
        ax.set_ylabel("Sentiment")
        fig.savefig(self.out_path + r"/sent_" + str(len(paragraph_sentiments)) + ".png")
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
        
        self.current_node = 0
        # (N^L-1) / (N-1)
        if self.storyGenerator.MAX_ACTIONS + self.addContinueButton == 1:
            self.total_nodes = self.storyGenerator.paragraphs
        else:
            self.total_nodes = ((self.storyGenerator.MAX_ACTIONS + self.addContinueButton) ** self.storyGenerator.paragraphs) / ((self.storyGenerator.MAX_ACTIONS-1 + self.addContinueButton))
        self.recursivelyContinue(f, paragraph, html_paragraph, inventory, "1", 1, self.EMPTY_ACTION, all_paragraphs, paragraph_coherences, paragraph_sentiments, paragraph_topics)

        f.write("The end\n")
        f.close()
        end_time = datetime.now()
        second_diff = (end_time - start_time).total_seconds()
        print("Started at " + str(start_time) + ", ended at " + str(end_time) + ", duration in seconds: " + str(second_diff))
        os.rename(self.out_path, self.out_path + "_done_in_" + str(second_diff))


    def recursivelyContinue(self, f, text, html, inventory, twineid, depth, action, all_paragraphs, paragraph_coherences, paragraph_sentiments, paragraph_topics):

        # generate twine paragraph id
        if twineid == "1":
            f.write("::Start\n")
            f.write("<<initInv>>")
            f.write(html)
        else:
            f.write("::" + str(twineid) + "\n")

        self.current_node += 1
        print("Calculating node " + str(self.current_node) + "/" + str(self.total_nodes) + " (depth: " + str(depth) + ") ...")

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
            paragraph_coherences.append(coh[0])
            paragraph_topics.append(coh[1][len(coh[1])-1])
            print("Coherence is: " + str(coh[0]))
            print("Topics are: " + str(coh[1][len(coh[1])-1]))

            sentiment = self.sentiment.sentiment(paragraph)
            paragraph_sentiments.append(sentiment)
            print("Sentiment is: " + str(sentiment))


            # Plot sentiment graph
            fig, ax = plt.subplots(nrows=1, ncols=1)
            ax.plot(range(0,len(paragraph_sentiments)), paragraph_sentiments)
            ax.set_xlabel("Paragraph")
            ax.set_ylabel("Sentiment")
            fig.savefig(self.out_path + r"/sent_" + str(twineid) + ".png")
            plt.close(fig)

            # Plot coherence graph
            fig, ax = plt.subplots(nrows=1, ncols=1)
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
        paragraph_coherences.append(coh[0])
        paragraph_topics.append(coh[1][len(coh[1])-1])
        print("Coherence is: " + str(coh[0]))
        print("Topics are: " + str(coh[1][len(coh[1])-1]))

        sentiment = self.sentiment.sentiment(paragraph)
        paragraph_sentiments.append(sentiment)
        print("Sentiment is: " + str(sentiment))

        # Plot sentiment graph
        fig, ax = plt.subplots(nrows=1, ncols=1)
        ax.plot(range(0,len(paragraph_sentiments)), paragraph_sentiments)
        ax.set_xlabel("Paragraph")
        ax.set_ylabel("Sentiment")
        fig.savefig(self.out_path + r"/sent_" + str(twineid) + ".png")
        plt.close(fig)

        # Plot coherence graph
        fig, ax = plt.subplots(nrows=1, ncols=1)
        ax.plot(range(0,len(paragraph_coherences)), paragraph_coherences)
        ax.set_xlabel("Paragraph")
        ax.set_ylabel("Coherence")
        image_path = self.out_path + r"/plt" + str(twineid) + ".png"
        fig.savefig(image_path)
        plt.close(fig)  

        # extract entities
        self.storyGenerator.extractEntities(paragraph)

        html_paragraph = paragraph

        f.write(html_paragraph + "\n<img style=\"width: 400px; height: auto;\" src=\"plt" + str(twineid) + ".png\"><br>")

        # Generate links
        if self.BERT_ACTIONS == True:
            actions = self.storyGenerator.generateActionsBert()
        else:
            actions = self.storyGenerator.generateActions()
        for idx, action in enumerate(actions):
            f.write("[[" + action["simple"] + "->" + twineid + "_" + str(idx) +"]]\n")

        # simple continue button
        if self.addContinueButton == 1 or len(actions) == 0:
            f.write("[[continue->" + twineid + "_" + str(len(actions))+"]]\n\n")
        for idx, action in enumerate(actions):
            # generate target for each action
            print("Generating action " + str(idx+1) + "/" + str(len(actions)) + "...")
            self.recursivelyContinue(f, text + paragraph, html + html_paragraph, inventory, twineid + "_" + str(idx), depth+1, action, all_paragraphs.copy(), paragraph_coherences.copy(), paragraph_sentiments.copy(), paragraph_topics.copy())

        # generate continue paragraph
        if self.addContinueButton == 1 or len(actions) == 0:
            if len(actions) == 0 and self.addContinueButton == 0:
                print("No plausible action found; adding a continue button.")
            self.recursivelyContinue(f, text + paragraph, html + html_paragraph, inventory, twineid + "_" + str(len(actions)), depth+1, self.EMPTY_ACTION, all_paragraphs.copy(), paragraph_coherences.copy(), paragraph_sentiments.copy(), paragraph_topics.copy())

if __name__ == '__main__':
    tg = TwineGenerator()
    tg.start()
