from item import items

class Combination:
    items = []
    returnItem = None
    action = ""
    simple_action = ""

    def __init__(self, items, returnItem):
        self.items = items
        self.returnItem = returnItem
        self.action = "[name] combined the " + ",".join([i.name for i in items[:-1]]) + " and the " + items[-1].name + " to receive a " + returnItem.description + "."
        self.simple_action = "Combine to " + returnItem.name


combinations = {
    "saw_sword" : Combination([items["plank"], items["saw"]], items["sword"])
}
