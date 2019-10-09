




# Define items
items = [saw, wood]
combinations = [
	[[saw,wood], boat, "Saw and wood were combined to a boat."]
]

# 1. Enter name and story length [# of paragraphs]

# 2. Select setting [middle age, fantasy, horror]
# -> Load individual checkpoints and items

# 3. Load/generate introduction [Place, Time, Crew, Items]
# -> place items in first place.

# 4. NLP on introduction [Extract People, Places, Items]

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