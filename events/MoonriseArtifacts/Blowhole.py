import utils.helper_functions as hf
from events.MoonriseArtifacts.Artifact import Artifact
from events.MoonriseCreatures.DarkForestCreature import DarkForestCreature


def increase_health(target: DarkForestCreature):
    """
    Increases the health of the active shield by 3000.
    :param target:
    :return:
    """
    hf.set_shield_damage(hf.get_shield_damage()-3000)
    hf.set_campfire_count(hf.get_campfire_count()-30)
    return "A blue-green torrent of pure void pours from the blowhole. The Salamander chirps as some of the water " \
           "splashes into the fire. As the deluge floods the Campgrounds, the trees surrounding it grow thicker," \
           "healing and hardening."


class Blowhole(Artifact):
    def __init__(self,
                 name="Eiyooooo's blowhole",
                 description="This thing is... well, it's a blowhole. How exactly Cicero extracted it is anyone's "
                             "guess, but now the thing is dried up and lightly emitting streams of vapor.",
                 uses=1,
                 cost="200l",
                 function=increase_health):
        Artifact.__init__(self, name, description, uses, cost, function)

    def use(self, *args):
        if self.uses > 0:
            self.uses -= 1
            return self.function(*args)
        else:
            return "The blowhole has shriveled, its last use expended."
