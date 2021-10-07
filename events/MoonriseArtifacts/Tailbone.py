from events.MoonriseArtifacts.Artifact import Artifact
from events.MoonriseCreatures.DarkForestCreature import DarkForestCreature

def summon_gidget(target: DarkForestCreature):

    return "The bone crumbles to dust as a small chihuahua appears next to you. In its mouth is a greasy paper bag " \
           "with the words 'Yo quiero Taco Bell' on it. Cicero shakes his head and grumbles about the " \
           "inevitability of late stage capitalism."


class Tailbone(Artifact):
    def __init__(self,
                 name="Tacolord Gidget's Tailbone",
                 description='This frightening large vertebrae must have come from  something truly massive. '
                             'As your fingers sweep across the hung of ossified flesh, you notice what appears to '
                             'be a bell carved into it. "Died of a grape, from what I understand." proclaims Cicero '
                             'mournfully.',
                 uses=1,
                 cost="100w",
                 function=summon_gidget):
        Artifact.__init__(self, name, description, uses, cost, function)

    def use(self, *args):
        if self.uses > 0:
            self.uses -= 1
            return self.function(*args)
        else:
            return "Gidget looks at you expectantly, surrounded by the pile of bone meal."
