from events.MoonriseArtifacts.Artifact import Artifact
from events.MoonriseCreatures.DarkForestCreature import DarkForestCreature


def macrosecond_timestop(target: DarkForestCreature):
    """
    Increases the health of the active shield by 3000.
    :param target:
    :return:
    """
    target.setAttackDelayMulti(target.get_attack_delay_multi() * 2)
    return "At Cicero's instruction. you jam a a stick into the grinding gears of the mechanical heart. Time slows," \
           " grinds to a halt, and then snaps forward. Everything except the interloper "


class Heart(Artifact):
    def __init__(self,
                 name="The Time-God's Heart",
                 description="Reluctantly, Cicero tells you about this. \"I found it long after the god in question"
                             " died. The corpse was just left in its temple, not even looted. It's been my most "
                             "faithful tool for a long time, but I've always meant to find another owner for it.\"",
                 uses=5,
                 cost="16000w",
                 function=macrosecond_timestop):
        Artifact.__init__(self, name, description, uses, cost, function)

    def use(self, *args):
        if self.uses > 0:
            self.uses -= 1
            return self.function(*args)
        else:
            return "The gears that make up the finally stop turning. It lies still in your hand. You can almost see a " \
                   "tear roll out of Cicero's mask."
