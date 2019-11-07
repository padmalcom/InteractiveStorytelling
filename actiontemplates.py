import random

class ActionTemplates:
    def getTemplate(self, action, player, entity):
        template = random.choice(actiontemplates[action])
        return template.replace("[name]", player).replace("[object]", entity)

actiontemplates = {
    "take" : ["Taking the [object] in both hands [name] stood there gratefully.", "[name] took the [object] with pride and smiled.", "Disgusted, [name] took the [object] from its place.", "[name] took the [object] without hesistation."]
}