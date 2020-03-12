import random

class ActionTemplates:
    def getTemplate(self, action, player, entity, entity_type):
        template = random.choice(actiontemplates[action])
        if (entity_type == "PERSON"):
            longaction = template.replace("[name]", player).replace("[object]", entity)
            simpleaction = simpleactions[action].replace("[name]", player).replace("[object]", entity)
        else:
            longaction = template.replace("[name]", player).replace("[object]", entity)
            simpleaction = simpleactions[action].replace("[name]", player).replace("[object]", entity)            
        return simpleaction, longaction

    def getUniversalTemplate(self, action, player, entity, entity_type):
        template = random.choice(universalactiontemplates)
        if (entity_type == "PERSON"):
            simpleaction = action + " " + entity
            longaction = template.replace("[name]", player).replace("the [object]", entity).replace("[predicate]", action)
        else:
            simpleaction = action + " the " + entity
            longaction = template.replace("[name]", player).replace("[object]", entity).replace("[predicate]", action)
        return simpleaction, longaction

actiontemplates = {
    "take" : ["Taking the [object] in both hands [name] stood there gratefully.", "[name] took the [object] with pride and smiled.", "Disgusted, [name] took the [object] from its place.", "[name] took the [object] without hesistation."],
    "talk to" : ["[name] spoke to [object].", "[name] took [object] aside and silently began to speak.", "[name] yelled at [object]."],
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

universalactiontemplates = [
    "[name] carefully [predicate] the [object].",
    "At first, [name] stood there for minutes before [predicate]ing the [object].",
    "With a mean smile, [name] [predicate] the [object].",
    "It took [name] like forever to [predicate] the [object]."

]

simpleactions = {
    "take":"[name] takes the [object].",
    "talk to":"[name] spoke to [object].",
    "compliment":"[name] compliments [object].",
    "insult":"[name] insults [object].",
    "look at":"[name] looks at [object].",
    "who are you,":"Who is [object]?",
    "go to":"[name] goes to [object].",
    "think about":"[name] thinks about [object].",
    "use":"[name] uses the [object].",
    "push":"[name] pushes the [object].",
    "pull":"[name] pulls the [object].",
    "open":"[name] opens the [object].",
    "close":"[name] closes the [object].",
    "talk to":"[name] talks to [object].",
    "use from inventory":"[name] uses the [object]."
}