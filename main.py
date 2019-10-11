from item import items
from combination import combinations
from setting import settings
import random
import spacy
import en_core_web_sm

if __name__ == '__main__':
	print("Welcome to PCG adventures!")

	# 1. Enter name and story length [# of paragraphs]
	name = input("Please enter your name: ")
	paragraphs = int(input("Welcome %s. How long should your journey be (# of paragraphs)? " % name))

	# 2. Select setting [middle age, fantasy, horror]
	# -> Load individual checkpoints and items
	setting = ""
	while True:
		setting = input("So %d paragraphs. And what setting do you prefer? [fantasy, sci-fy] " % paragraphs)
		if setting in settings.keys():
			break
		else:
			print("Please enter a setting name.")
	print("So our story takes place in a %s world." % setting)

	# 3. Load/generate introduction [Place, Time, Crew, Items]
	# -> place items in first place.
	introduction = random.choice(settings[setting].introductions)

	# Replace [name]
	introduction = introduction.replace("[name]", name)
	print(introduction)

	# 4. NLP on introduction [Extract People, Places, Items]
	inventory = []
	nlp = spacy.load("en_core_web_sm")
	doc = nlp(introduction)

	for ent in doc.ents:
		print(ent.text, ent.start_char, ent.end_char, ent.label_)


# 5. Extract relation of characters

# 6. Generate actions [Talk to, Take [item] {based on nlp}, go to [Place], Inspect [Item, Place, Person, Item in inventory], Push, Pull {fun?},
# insult/compliment [Person], use [item], combine [item, item]]

# 7. Write twine paragraph including actions

# 8. Wait for player input

# 9. React to input and update meta data [add [place] to [known places], add [items], set [location], remove [item]]

# 10. Truncate text

# 11. Increase paragraph counter
# -> If end reached add text "So this is the end of our story."

# 12. Generate following paragraph
# If end is not reached -> Goto 4