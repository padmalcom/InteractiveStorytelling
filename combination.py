from item import items

class Combination:
    items = []
    returnItem = None
    description = "Items have been combined."

    def __init__(self, items, returnItem, description):
        self.items = items
        self.returnItem = returnItem
        self.description = description


combinations = {
    "saw_sword" : Combination([items["wood_plank"], items["saw"]], items["wooden_sword"], "It was easy to cut the wooden plank with the saw to a simple, wodden sword.")
}
