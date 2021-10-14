from events.MoonriseArtifacts.Artifact import Artifact, load_status, update_status
from events.MoonriseCreatures.DarkForestCreature import DarkForestCreature
import utils.helper_functions as hf

moonrise_status_dir = hf.settings["directories"]["moonrise_status"]


def slaying(target: DarkForestCreature):
    """
    Causes the creature to skip its turn if its name begins with an S
    :param target:
    :return:
    """

    if target.name[0].lower() == 's':
        data = load_status()

        data['artifact_effects'].append('slaying')

        update_status(data)
        target.setHealth(int(target.getHealth()*0.8))

        return "The scales flash and one of the words blurs out, but nothing happens immediately."
    else:
        return "The scale shimmers briefly, but nothing happens."


class Scale(Artifact):
    def __init__(self,
                 name="S.wallow's S.cales",
                 description="These scales are a deep shimmering blue, and shaped like paddle-like swords. "
                             "Each one has a word written on it, starting with S. \"Hm? Oh"
                             " yes, S.wallow. Like Rathym, a god of tricks. Unlike Rathym, it knew when to stop. "
                             "These scales are the only thing that was left of its corporeal form when I found it.",
                 uses=30,
                 cost="2000w",
                 function=slaying):
        Artifact.__init__(self, name, description, uses, cost, function)

    def use(self, *args):
        if self.uses > 0:
            self.uses -= 1
            return self.function(*args)
        else:
            return "All of the scales have lost their luster. The words that were scrawled on each one have become " \
                   "faded and unreadable."
