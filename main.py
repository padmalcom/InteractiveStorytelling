from item import items
from combination import combinations
from setting import settings
import random
import spacy
import en_core_web_lg
import gpt_2_simple as gpt2

# pyqt5
from PyQt5.QtWidgets import *
import sys

if __name__ == '__main__':

	# initialization
	inventory = []
	known_places = []
	known_people = []
	nlp = spacy.load("en_core_web_lg")
	name = ""
	paragraphs = 0
	setting = ""
	introduction = ""
	items_in_paragraph = []
	places_in_paragraph = []
	people_in_paragraph = []
	events_in_paragraph = []
	text = ""

	# initialize gpt-2
	session = gpt2.start_tf_sess()
	gpt2.load_gpt2(session)

	print("Welcome to PCG adventures!")

	# 1. Enter name and story length [# of paragraphs]
	name = input("Please enter your name: ")
	paragraphs = int(input("Welcome %s. How long should your journey be (# of paragraphs)? " % name))

	# 2. Select setting [middle age, fantasy, horror]
	# -> Load individual checkpoints and items
	while True:
		setting = input("So %d paragraphs. And what setting do you prefer? [fantasy, sci-fy] " % paragraphs)
		if setting in settings.keys():
			break
		else:
			print("Please enter a setting name.")
	print("So our story takes place in a %s world." % setting)

	# 3. Load/generate introduction [Place, Time, Crew, Items]
	# -> place items in first place.
	paragraph = random.choice(settings[setting].introductions)

	paragraph_count = 0

	while paragraph_count < paragraphs:

		# Replace [name]
		paragraph = paragraph.replace("[name]", name)
		print(paragraph)

		# append paragraph
		text = text + paragraph

		# 4. NLP on paragraph [Extract People, Places, Items]
		doc = nlp(paragraph)

		# 4.1 clear entities before extraction
		people_in_paragraph.clear()
		places_in_paragraph.clear()
		events_in_paragraph.clear()
		items_in_paragraph.clear()

		# 4.2 extract each entity
		for ent in doc.ents:
			print(ent.text, ent.start_char, ent.end_char, ent.label_)
			if ent.label_ == "PERSON" and ent.text != name:
				people_in_paragraph.append(ent.text)
			elif ent.label_ == "GPE" or ent.label_ == "LOC":
				places_in_paragraph.append(ent.text)
			elif ent.label_ == "EVENT": # talk about event
				events_in_paragraph.append(ent.text)
			elif ent.label_ == "PRODUCT":
				items_in_paragraph.append(ent.text)
		
		# 5. Check if none or only the main character is named as ent
		if (people_in_paragraph.count() > 0 or places_in_paragraph.count() > 0 or events_in_paragraph.count() > 0 or items_in_paragraph() > 0):

			# 6. Generate actions [Talk to, Take [item] {based on nlp}, go to [Place], Inspect [Item, Place, Person, Item in inventory], Push, Pull {fun?},
			# insult/compliment [Person], use [item], combine [item, item]]
			for person in people_in_paragraph:
				print("[talk to %s]"%person)
				print("[look to %s]"%person)
				print("[insult to %s]"%person)
				print("[compliment to %s]"%person)
				print("[%s who are you?]"%person)
			for place in places_in_paragraph:
				print("[go to %s]"%place)
				print("[inspect %s]"%place)
			for event in events_in_paragraph:
				print("[Think about %s]"%event)
			for item in items_in_paragraph:
				print("[take %s]"%item)
				print("[use %s]"%item)
				print("[push %s]"%item)

		else:
			# 6.2 Just generate another paragraph
			print("[continue]")

		#text = gpt2.generate(session, temperature=0.1,prefix=text,run_name='run1',length=100,return_as_list=True,nsamples=3,batch_size=3,top_p=0.99)
				
		# 7. Write twine paragraph including actions

		# 8. Wait for player input

		# 9. React to input and update meta data [add [place] to [known places], add [items], set [location], remove [item]]

		# 10. Truncate text

		# 11. Increase paragraph counter
		paragraph_count +=1

		# -> If end reached add text "So this is the end of our story."

		# 12. Generate following paragraph
		# If end is not reached -> Goto 4