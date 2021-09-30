import utils.helper_functions as hf
from events.MoonriseArtifacts.Artifact import Artifact
from events.MoonriseCreatures.DarkForestCreature import DarkForestCreature


def crescendo(target: DarkForestCreature):
    """
    Increases the health of the active shield by 3000.
    :param target:
    :return:
    """
    target.setHealth(400)
    target.setBaseAttackStrength(100)
    target.setBaseAttackDelay(10)
    return "The finger twitches and flops in your hand. It points at the incoming monster and plucks an invisible " \
           "string. The creature's limbs snap, then reform as muscles thicken. Now a strange mass of undulating " \
           "sinew and broken bones, it renews its charge."


class Finger(Artifact):
    def __init__(self,
                 name="Rathym's Twitching Finger",
                 description="Once, this finger belonged to a god of music and mischief, Rathym. One of the other gods"
                             " eventually ran out of patience with Rathym's tricks and seperated each finger"
                             " from his hand. It still twitches to this day, searching for the strings it used to "
                             "pluck.",
                 uses=1,
                 cost="200w",
                 function=crescendo):
        Artifact.__init__(self, name, description, uses, cost, function)

    def use(self, *args):
        if self.uses > 0:
            self.uses -= 1
            return self.function(*args)
        else:
            return "The finger has finally ceased its twitching, its last song finished."
