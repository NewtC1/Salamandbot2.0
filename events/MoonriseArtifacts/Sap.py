from events.MoonriseArtifacts.Artifact import Artifact
from events.MoonriseCreatures.DarkForestCreature import DarkForestCreature


def time_reverse(target: DarkForestCreature):
    """
    Restores one use on all users artifacts
    :param target:
    :return:
    """
    pass


class Sap(Artifact):
    def __init__(self,
                 name="Sap of the Tree of Wounds",
                 description='The light that passes through this bloody, viscous liquid comes out purple, regardless'
                             ' of its original color. "Harvested locally. Do not ingest." Looking up, it\'s hard to '
                             'tell if Cicero is joking or not.',
                 uses=2,
                 cost="2000w",
                 function=time_reverse):
        Artifact.__init__(self, name, description, uses, cost, function)

    def use(self, *args):
        if self.uses > 0:
            self.uses -= 1
            return self.function(*args)
        else:
            return "The tusk has disintegrated, unable to maintain its form when separated from its body."
