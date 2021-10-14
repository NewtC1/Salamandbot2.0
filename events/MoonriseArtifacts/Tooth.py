from events.MoonriseArtifacts.Artifact import Artifact
from events.MoonriseCreatures.DarkForestCreature import DarkForestCreature


def bite(target: DarkForestCreature):
    """
    :param target: The DarkForestCreature to remove armor from.
    :return:
    """
    damage = 30
    target.setHealth(target.getHealth() - damage)
    return 'The teeth shiver in your hand, then form into the grisly, bloodstained smile of a wolf. One of the teeth ' \
           'leaps out of your palm and into the oncoming creature, chewing through flesh and bone alike.'


class Tooth(Artifact):
    def __init__(self,
                 name="Ungmar's teeth",
                 description='\"One of the most hated gods on the world I found him. Apparently the other gods disliked '
                             'him so much that they killed him and consumed his remains. I found these in their... '
                             'well, scat.\"',
                 uses=42,
                 cost="150w",
                 function=bite):
        Artifact.__init__(self, name, description, uses, cost, function)

    def use(self, *args):
        if self.uses > 0:
            self.uses -= 1
            return self.function(*args)
        else:
            return "All of the teeth have embedded themselves in targets. There's no getting them back now."
