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
import numpy as np
import pandas as pd
from sentiment import Sentiment
import logging
import logging.config
import itertools
import gender_guesser.detector as gender


class TwineGenerator():
    def __init__(self):
        super().__init__()
        self.storyGenerator = StoryGenerator()
        self.action_buttons = []
        self.inventory_labels = []
        self.out_path = ""

        self.storyGenerator.CHANCE_TO_REMEMBER_ITEM = 0.0
        self.storyGenerator.CHANCE_TO_REMEMBER_PERSON = 0.0

        self.total_nodes = 0
        self.current_node = 0

        self.EMPTY_ACTION = {"type":"", "action":"", "entity":"", "sentence":"", "simple": "", "probability":""}

        self.action_generator = 0

        self.DEBUG_OUT = True
        self.REACT_TO_SENTIMENT = False
        self.MAX_CHARACTERS = 8

        self.sentiment = Sentiment()

        self.GENDER_A = ["unknown", "androgynous", "male", "mostly_male"]

        self.gender_detector = gender.Detector()
        logging.basicConfig(level=logging.DEBUG)
        logging.config.dictConfig({'version': 1, 'disable_existing_loggers': True})
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initialization done.")

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

        self.action_generator = int(input("Select an action generator (0 NLP, 1 MASK, 2 GENERATIVE): "))
        if self.action_generator != 0 and self.action_generator != 1 and self.action_generator != 2:
            print("Invalid action generator. Setting to NLP.")
            self.action_generator = 0

        if (self.addContinueButton != 0 and self.addContinueButton != 1):
            self.addContinueButton = 0
            self.logger.debug("Continue button was disabled due to an invalid input.")

        self.storyGenerator.setting_id = random.randrange(0, len(self.storyGenerator.getSettings()[self.storyGenerator.setting].introductions))
        self.storyGenerator.setting_id = 0 # temporary

        all_paragraphs = []
        paragraph_coherences = []
        paragraph_sentiments = []
        paragraph_topics = []
        paragraph_actions = []
        paragraph_characters = []

        inventory = []

        # Where is the story stored?
        self.out_path = r"C:/Users/admin/" + datetime.now().strftime("story_%d.%m.%Y_%H-%M-%S")+ "_para" + str(self.storyGenerator.paragraphs)
        if os.path.exists(self.out_path):
            self.logger.error("Story directory already exists. Exiting")
        else:
            os.mkdir(self.out_path)
        
        # do not use self.storyGenerator.paragraph since we are in a tree structure
        paragraph = self.storyGenerator.getSettings()[self.storyGenerator.setting].introductions[self.storyGenerator.setting_id]

        paragraph = paragraph.replace("[name]", self.storyGenerator.name)
        all_paragraphs.append(paragraph)
        coh = self.storyGenerator.calculateParagraphCoherence(all_paragraphs)
        paragraph_coherences.append(coh[0])
        paragraph_topics.append(coh[1][len(coh[1])-1])
        self.logger.debug("Coherence is: " + str(coh[0]))
        self.logger.debug("Topics are: " + str(coh[1][len(coh[1])-1]))

        sentiment = self.sentiment.sentiment(paragraph)
        paragraph_sentiments.append(sentiment)
        self.logger.debug("Sentiment is: " + str(sentiment))

        # Plot coherence graph
        if self.DEBUG_OUT:
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
        paragraph_characters.append(self.storyGenerator.people_in_paragraph.copy())
        paragraph_characters[len(paragraph_characters)-1].append(self.storyGenerator.name)
        
        self.current_node = 0
        # (N^L-1) / (N-1)
        if self.storyGenerator.MAX_ACTIONS + self.addContinueButton == 1:
            self.total_nodes = self.storyGenerator.paragraphs
        else:
            self.total_nodes = ((self.storyGenerator.MAX_ACTIONS + self.addContinueButton) ** self.storyGenerator.paragraphs - 1) / (self.storyGenerator.MAX_ACTIONS-1 + self.addContinueButton)
        self.recursivelyContinue(f, paragraph, html_paragraph, inventory, "1", 1, self.EMPTY_ACTION, all_paragraphs,
            paragraph_coherences, paragraph_sentiments, paragraph_topics, paragraph_actions, paragraph_characters)

        f.close()
        end_time = datetime.now()
        second_diff = (end_time - start_time).total_seconds()
        self.logger.info("Started at " + str(start_time) + ", ended at " + str(end_time) + ", duration in seconds: " + str(second_diff))
        os.rename(self.out_path, self.out_path + "_done_in_" + str(second_diff))


    def recursivelyContinue(self, f, text, html, inventory, twineid, depth, action, all_paragraphs, paragraph_coherences,
        paragraph_sentiments, paragraph_topics, paragraph_actions, paragraph_characters):

        start_time_batch = datetime.now()

        # generate twine paragraph id
        if twineid == "1":
            f.write("::Start\n")
            f.write("<<initInv>>")
            f.write(html)
        else:
            f.write("::" + str(twineid) + "\n")

        self.current_node += 1
        self.logger.info("Calculating node " + str(self.current_node) + "/" + str(self.total_nodes) + " (depth: " + str(depth) + ") ...")

        # end reached?
        if (depth == self.storyGenerator.paragraphs):
            end_text, _ = self.storyGenerator.generateEnd()
            text = text + " " + action["sentence"] + " " + end_text
            truncated_text = self.storyGenerator.truncateLastSentences(text, self.storyGenerator.TRUCATED_LAST_TEXT)
            try:
                new_text = self.storyGenerator.generateText(truncated_text)
            except:
                self.logger.error("0 Generation error on truncated_text: '" + truncated_text + "'")
                new_text = ""
            paragraph = action["sentence"] + " " + end_text + " " + new_text

            self.storyGenerator.extractEntities(paragraph)
            

            # replace new characters?
            if (self.MAX_CHARACTERS > -1):

                all_characters = list(set(list(itertools.chain.from_iterable(paragraph_characters))))

                new_characters = [x for x in self.storyGenerator.people_in_paragraph if x not in all_characters]

                print("All characters: " + str(all_characters))
                print("New characters: " + str(new_characters))

                if len(all_characters) + len(new_characters) > self.MAX_CHARACTERS:
                    logging.info("There are more (" + str(len(all_characters) + len(new_characters)) + ") characters"
                        + " in the story than allowed. Replacing...")
                    chars_to_replace = len(all_characters) + len(new_characters) - self.MAX_CHARACTERS
                    if self.storyGenerator.name in all_characters:
                        all_characters.remove(self.storyGenerator.name)
                    if self.storyGenerator.party1 in all_characters:
                        all_characters.remove(self.storyGenerator.party1)
                    if self.storyGenerator.party2 in all_characters:
                        all_characters.remove(self.storyGenerator.party2)

                    group_a = [x for x in all_characters if self.gender_detector.get_gender(x) in self.GENDER_A]
                    group_b = [x for x in all_characters if self.gender_detector.get_gender(x) not in self.GENDER_A]

                    if (len(group_a) == 0):
                        print("Names of group a are empty.")
                        group_a.extend(group_b.copy())
                    if (len(group_b) == 0):
                        print("Names of group b are empty.")
                        group_b.extend(group_a.copy())

                    if len(group_a) > 0 and len(group_b) > 0:
                        for char in new_characters:
                            gender = self.gender_detector.get_gender(char)
                            if gender in self.GENDER_A:
                                replacement_name = random.choice(group_a)
                                if len(group_a) > 1:
                                    group_a.remove(replacement_name)
                            else:
                                replacement_name = random.choice(group_b)
                                if len(group_b) > 1:
                                    group_b.remove(replacement_name)
                            print("Replacing " + char + " with " + replacement_name)
                            paragraph = paragraph.replace(char, replacement_name)
                            self.storyGenerator.people_in_paragraph = [p.replace(char, replacement_name) for p in self.storyGenerator.people_in_paragraph]
                            chars_to_replace = chars_to_replace - 1
                            if chars_to_replace <= 0:
                                break
                    else:
                        print("Cannot replace, replacement names are empty.")

            html_paragraph = paragraph
            
            # coherence
            #all_paragraphs.append(new_text) # This is wrong since action is not appended
            all_paragraphs.append(paragraph)
            coh = self.storyGenerator.calculateParagraphCoherence(all_paragraphs)
            paragraph_coherences.append(coh[0])
            paragraph_topics.append(coh[1][len(coh[1])-1])
            self.logger.debug("Coherence is: " + str(coh[0]))
            self.logger.debug("Topics are: " + str(coh[1][len(coh[1])-1]))

            sentiment = self.sentiment.sentiment(paragraph)
            paragraph_sentiments.append(sentiment)
            self.logger.debug("Sentiment is: " + str(sentiment))


            # Plot sentiment graph
            if self.DEBUG_OUT:
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
                fig.savefig(self.out_path + r"/coh_" + str(twineid) + ".png")
                plt.close(fig)

                # log coherences to file
                with open(self.out_path + r"/coherence.txt", 'a') as coh_file:
                    for idx,c in enumerate(paragraph_coherences):
                        coh_file.write(str(idx) + '\t' + str(c) + '\n')

            # highlight entities and names
            html_paragraph = self.storyGenerator.highlightEntities(html_paragraph)
            html_paragraph = html_paragraph.replace(self.storyGenerator.name, "<b>" + self.storyGenerator.name + "</b>")
            paragraph_characters.append(self.storyGenerator.people_in_paragraph.copy())
            paragraph_characters[len(paragraph_characters)-1].append(self.storyGenerator.name)

            if self.DEBUG_OUT:
                # https://stackoverflow.com/questions/50821484/python-plotting-missing-data
                distinct_characters = []
                for chars in paragraph_characters:
                    for char in chars:
                        if not char in distinct_characters:
                            distinct_characters.append(char)
                self.logger.debug("Distinct chars: " + str(distinct_characters))

                paragraph_list = range(len(paragraph_characters))
                character_presences = []
                for idx1, char in enumerate(distinct_characters):
                        cp = []
                        for idx, pc in enumerate(paragraph_characters):
                            if char in pc:
                                cp.append(idx1)
                            else:
                                cp.append(np.nan)
                        character_presences.append(cp)
                #self.logger.debug("Character presences: " + str(character_presences))

                character_dict = dict()
                for idx, cp in enumerate(character_presences):
                    character_dict[distinct_characters[idx]] = cp
                df = pd.DataFrame(character_dict, index = paragraph_list)
                df.index.name = 'paragraphs'

                fig, ax = plt.subplots()
                fig.set_figheight(15)
                fig.set_figwidth(15)
                
                for key in character_dict:
                    line, = ax.plot(df[key].fillna(method='ffill'), ls = '--', lw = 1, label='_nolegend_')
                    ax.plot(df[key], color=line.get_color(), lw=1.5, marker = 'o')
                
                plt.xticks(range(len(paragraph_characters)))
                plt.yticks(range(len(distinct_characters)))               

                plt.xlabel('paragraph')
                plt.ylabel('character')

                # replace labels
                labels=ax.get_yticks().tolist()
                for idx, char in enumerate(distinct_characters):
                    labels[idx] = char
                ax.set_yticklabels(labels)

                fig.savefig(self.out_path + r"/char_" + str(twineid) + ".png")
                plt.close(fig)


            # finally append entire text
            text = text + " " + paragraph
            html = html + " " + html_paragraph
            

            f.write(html_paragraph + "<br>")

            if len(paragraph_topics) > 0 and self.DEBUG_OUT:
                f.write("<table bordercolor=\"white\" style=\"width: 100%\"><tr><td><b>Topics:</b></td><td>" + ", ".join(paragraph_topics[len(paragraph_topics)-1]) + "</td></tr></table><br>")

            if self.DEBUG_OUT:   
                f.write("<img style=\"width: 400px; height: auto;\" src=\"coh_" + str(twineid) + ".png\">" +
                    "<img style=\"width: 400px; height: auto;\" src=\"sent_" + str(twineid) + ".png\">" +
                    "<img style=\"width: 400px; height: auto;\" src=\"char_" + str(twineid) + ".png\">" +
                    "<br>")                     

            f.write("\n<b>THE END</b>\n")
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
                self.logger.debug("Trying to remove " + action["entity"] + " but not in inv.")

        # Store the action in paragraph actions
        if action["simple"] != "":
            paragraph_actions.append(action["simple"])

        # generate next paragraph
        text = text + " " + action["sentence"]
        truncated_text = self.storyGenerator.truncateLastSentences(text, self.storyGenerator.TRUCATED_LAST_TEXT)
        try:
            if self.REACT_TO_SENTIMENT:
                if paragraph_sentiments[len(paragraph_sentiments)-1] == 1:
                    truncated_text = truncated_text + ". Luckyly, "
                else:
                    truncated_text = truncated_text + ". Unfortunately, "
            new_text = self.storyGenerator.generateText(truncated_text)
        except:
            self.logger.error("1 Generation error on truncated_text: '" + truncated_text + "'")
            new_text = ""
            
        paragraph = action["sentence"] + " " + new_text

        # extract entities
        self.storyGenerator.extractEntities(paragraph)

        # replace new characters?
        if (self.MAX_CHARACTERS > -1):

            all_characters = list(set(list(itertools.chain.from_iterable(paragraph_characters))))

            new_characters = [x for x in self.storyGenerator.people_in_paragraph if x not in all_characters]

            print("All characters: " + str(all_characters))
            print("New characters: " + str(new_characters))

            if len(all_characters) + len(new_characters) > self.MAX_CHARACTERS:
                logging.info("There are more (" + str(len(all_characters) + len(new_characters)) + ") characters"
                    + " in the story than allowed. Replacing...")
                chars_to_replace = len(all_characters) + len(new_characters) - self.MAX_CHARACTERS
                if self.storyGenerator.name in all_characters:
                    all_characters.remove(self.storyGenerator.name)
                if self.storyGenerator.party1 in all_characters:
                    all_characters.remove(self.storyGenerator.party1)
                if self.storyGenerator.party2 in all_characters:
                    all_characters.remove(self.storyGenerator.party2)

                group_a = [x for x in all_characters if self.gender_detector.get_gender(x) in self.GENDER_A]
                group_b = [x for x in all_characters if self.gender_detector.get_gender(x) not in self.GENDER_A]

                if (len(group_a) == 0):
                    print("Names of group a are empty.")
                    group_a.extend(group_b.copy())
                if (len(group_b) == 0):
                    print("Names of group b are empty.")
                    group_b.extend(group_a.copy())

                if len(group_a) > 0 and len(group_b) > 0:
                    for char in new_characters:
                        gender = self.gender_detector.get_gender(char)
                        if gender in self.GENDER_A:
                            replacement_name = random.choice(group_a)
                            if len(group_a) > 1:
                                group_a.remove(replacement_name)
                        else:
                            replacement_name = random.choice(group_b)
                            if len(group_b) > 1:
                                group_b.remove(replacement_name)
                        print("Replacing " + char + " with " + replacement_name)
                        paragraph = paragraph.replace(char, replacement_name)
                        self.storyGenerator.people_in_paragraph = [p.replace(char, replacement_name) for p in self.storyGenerator.people_in_paragraph]
                        chars_to_replace = chars_to_replace - 1
                        if chars_to_replace <= 0:
                            break
                else:
                    print("Cannot replace, replacement names are empty.")
        
        #all_paragraphs.append(new_text) This is wrong since the action is not appended!
        all_paragraphs.append(paragraph)
        coh = self.storyGenerator.calculateParagraphCoherence(all_paragraphs)
        paragraph_coherences.append(coh[0])
        paragraph_topics.append(coh[1][len(coh[1])-1])
        self.logger.debug("Coherence is: " + str(coh[0]))
        self.logger.debug("Topics are: " + str(coh[1][len(coh[1])-1]))

        sentiment = self.sentiment.sentiment(paragraph)
        paragraph_sentiments.append(sentiment)
        self.logger.debug("Sentiment is: " + str(sentiment))

        # Plot sentiment graph
        if self.DEBUG_OUT:
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
            image_path = self.out_path + r"/coh_" + str(twineid) + ".png"
            fig.savefig(image_path)
            plt.close(fig)  



        html_paragraph = paragraph
        html_paragraph = self.storyGenerator.highlightEntities(html_paragraph)
        html_paragraph = html_paragraph.replace(self.storyGenerator.name, "<b>" + self.storyGenerator.name + "</b>")
        paragraph_characters.append(self.storyGenerator.people_in_paragraph.copy())
        paragraph_characters[len(paragraph_characters)-1].append(self.storyGenerator.name)

        if self.DEBUG_OUT:
            # https://stackoverflow.com/questions/50821484/python-plotting-missing-data
            distinct_characters = []
            for chars in paragraph_characters:
                for char in chars:
                    if not char in distinct_characters:
                        distinct_characters.append(char)
            self.logger.debug("Distinct chars: " + str(distinct_characters))

            paragraph_list = range(len(paragraph_characters))
            character_presences = []
            for idx1, char in enumerate(distinct_characters):
                    cp = []
                    for idx, pc in enumerate(paragraph_characters):
                        if char in pc:
                            cp.append(idx1)
                        else:
                            cp.append(np.nan)
                    character_presences.append(cp)
            #self.logger.debug("Character presences: " + str(character_presences))

            character_dict = dict()
            for idx, cp in enumerate(character_presences):
                character_dict[distinct_characters[idx]] = cp
            df = pd.DataFrame(character_dict, index = paragraph_list)
            df.index.name = 'paragraphs'

            fig, ax = plt.subplots()
            fig.set_figheight(15)
            fig.set_figwidth(15)
            
            for key in character_dict:
                line, = ax.plot(df[key].fillna(method='ffill'), ls = '--', lw = 1, label='_nolegend_')
                ax.plot(df[key], color=line.get_color(), lw=1.5, marker = 'o')
            
            plt.xticks(range(len(paragraph_characters)))
            plt.yticks(range(len(distinct_characters)))

            plt.xlabel('paragraph')
            plt.ylabel('character')

            # replace labels
            labels=ax.get_yticks().tolist()
            for idx, char in enumerate(distinct_characters):
                labels[idx] = char
            ax.set_yticklabels(labels)

            fig.savefig(self.out_path + r"/char_" + str(twineid) + ".png")
            plt.close(fig)

        f.write(html_paragraph + "<br>")
        
        if len(paragraph_topics) > 0 and self.DEBUG_OUT:
            f.write("<table bordercolor=\"white\" style=\"width: 100%\"><tr><td><b>Topics:</b></td><td>" + ", ".join(paragraph_topics[len(paragraph_topics)-1]) + "</td></tr></table><br>")
        
        if self.DEBUG_OUT:
            f.write("<img style=\"width: 400px; height: auto;\" src=\"coh_" + str(twineid) + ".png\">" +
                "<img style=\"width: 400px; height: auto;\" src=\"sent_" + str(twineid) + ".png\">" +
                "<img style=\"width: 400px; height: auto;\" src=\"char_" + str(twineid) + ".png\">" +
                "<br>")

        # Generate links
        if self.action_generator == 1:
            actions = self.storyGenerator.generateActionsBert(paragraph_actions, True)
        elif self.action_generator == 2:
            actions = self.storyGenerator.generateActionsGPT2(paragraph, self.storyGenerator.MAX_ACTIONS, paragraph_actions)
        else:
            actions = self.storyGenerator.generateActions(paragraph_actions)

        for idx, action in enumerate(actions):
            f.write("[[" + action["order"] + "->" + twineid + "_" + str(idx) +"]]\n")

        end_time_batch = datetime.now()

        self.logger.debug("This run took " + str(end_time_batch - start_time_batch) + " milliseconds.")

        # simple continue button
        if self.addContinueButton == 1 or len(actions) == 0:
            f.write("[[continue->" + twineid + "_" + str(len(actions))+"]]\n\n")
        for idx, action in enumerate(actions):
            # generate target for each action
            self.logger.debug("Generating action " + str(idx+1) + "/" + str(len(actions)) + "...")
            self.recursivelyContinue(f, text + paragraph, html + html_paragraph, inventory, twineid + "_" + str(idx),
                depth+1, action, all_paragraphs.copy(), paragraph_coherences.copy(), paragraph_sentiments.copy(),
                paragraph_topics.copy(), paragraph_actions.copy(), paragraph_characters.copy())

        # generate continue paragraph
        if self.addContinueButton == 1 or len(actions) == 0:
            if len(actions) == 0 and self.addContinueButton == 0:
                self.logger.debug("No plausible action found; adding a continue button.")
            self.recursivelyContinue(f, text + paragraph, html + html_paragraph, inventory, twineid + "_" + str(len(actions)),
                depth+1, self.EMPTY_ACTION, all_paragraphs.copy(), paragraph_coherences.copy(),
                paragraph_sentiments.copy(), paragraph_topics.copy(), paragraph_actions.copy(), paragraph_characters.copy())

if __name__ == '__main__':
    tg = TwineGenerator()
    tg.start()
