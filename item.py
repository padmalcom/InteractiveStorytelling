class Item:
    name = ""
    description = ""
    category = ""

    def __init__(self, name, description, category):
        self.name = name
        self.description = description
        self.category = category



items = {
    "bottle" : Item("bottle", "a green bottle containing water.", "fantasy"),
    "fairy_in_jar" : Item("fairy in jar", "a tiny fairy in a jar.", "fantasy"),
    "wood_plank" : Item("wooden plank", "an old wooden plank.", "fantasy"),
    "saw" : Item("saw", "an old, rusty saw.", "fantasy"),
    "wooden_sword" : Item("wooden sword", "a short but sharp wooden sword.", "fantasy")
}