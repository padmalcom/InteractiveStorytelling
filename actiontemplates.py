import random

class ActionTemplates:
    def getTemplate(self, action, player, entity):
        template = random.choice(actiontemplates[action])
        return template.replace("[name]", player).replace("[object]", entity)

actiontemplates = {
    "take" : ["Taking the [object] in both hands [name] stood there gratefully.", "[name] took the [object] with pride and smiled.", "Disgusted, [name] took the [object] from its place.", "[name] took the [object] without hesistation."],
    "compliment":["[name] shyly complimented [object].", "Ironically, [name] complimented [object]."],
    "insult":["[name] insulted [object] in the worst possible way.", "[name] said [object] was the dumbest creature living under the sun."],
    "look at":["[name] looked at [object] carefully.", "With an irrepressible curiosity, [name] looked at [object]."],
    "who are you,":["\"[object], who are you?\", asked [name]."],
    "go to":["[name] decided to go to [object].", "Time to go. [name] started his way to [object]."],
    "think about":["[name] thought about [object].", "Frowning [name] thought about what the [object] was all about."],
     "use":["[name] was convinced that using the [object] was a good idea.", "[name] used the [object] without hesistation."],
     "push":["[name] pushed the [object] hard.", "Carefully, [name] pushed the [object]."],
     "pull":["With only two fingers [name] pulled the [object].", "The [object] didn't say pull, but [name] pulled."],
     "open":["Carefully, [name] opened the [object]."],
     "close":["With a smash, [name] closed the [object]."],
     "talk to":["[name] decided to talk to [object].", "\"Hey, [object], I want to talk\", said [name]."],
     "use from inventory":["[name] used the [object] from the inventory.", "[name] pulled out the [object] from the bag and used it."]
}