from events.MoonriseArtifacts.Artifact import Artifact
from events.MoonriseCreatures.DarkForestCreature import DarkForestCreature


def break_armor(target: DarkForestCreature):
    """
    :param target: The DarkForestCreature to remove armor from.
    :return:
    """
    damage = 2

    if target.GetIncResist() >= damage:
        target.SetIncResist(target.GetIncResist() - damage)
    else:
        target.SetIncResist(0)
    return "The tusk surges with power, and its corrupting entropy breaks against the creature's armor, " \
           "shearing it away."


class Tusk(Artifact):
    def __init__(self,
                 name="Tusk of the Starlight Boar",
                 description='A long curved tooth, with a strange, sparkling dust fuming from it. '
                             'Reality corrodes around it. "A curious one. A god of entropy who\'s followers preached'
                             ' the love of life. Ironically, it died when it fulfilled its fated role."',
                 uses=3,
                 cost="50l",
                 function=break_armor):
        Artifact.__init__(self, name, description, uses, cost, function)

    def use(self, *args):
        if self.uses > 0:
            self.uses -= 1
            return self.function(*args)
        else:
            return "The tusk has disintegrated, unable to maintain its form when separated from its body."
