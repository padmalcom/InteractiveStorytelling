class Item:
    name = ""
    description = ""
    category = ""

    def __init__(self, name, description):
        self.name = name
        self.description = description


items = {
    "bottle" : Item("bottle", "a green bottle containing water."),
    "jar" : Item("fairy in jar", "a tiny fairy in a jar."),
    "plank" : Item("wooden plank", "an old wooden plank."),
    "saw" : Item("saw", "an old, rusty saw."),
    "sword" : Item("wooden sword", "a short but sharp wooden sword."),
    "light" : Item("tiny light", "a tiny but bright light.")
}