from events.MoonriseArtifacts.Artifact import Artifact, load_status, update_status
from events.MoonriseCreatures.DarkForestCreature import DarkForestCreature


def folded_world(target: DarkForestCreature):
    """
    Causes the creature to skip its turn if its name begins with an S
    :param target:
    :return:
    """

    if target.name[0].lower() == 's':
        data = load_status()

        data['folded_world'] = True

        update_status(data)
        target.setHealth(int(target.getHealth()*0.8))

        return "The shard cracks, splinters, and then folds in upon itself. A strange crease remains in the air " \
               "where it once sat. If you squint, you can just make out the branches and wrinkles expanding from " \
               "that crease."


class Shard(Artifact):
    def __init__(self,
                 name="Shard of the Victor",
                 description="In this shard of a broken world, you catch a glimpse of an alternate universe. This "
                             "forest was tamed, the monsters were broken, and the forgotten one stands triumphant. "
                             "\"Shame about that one."
                             " You've forgotten it, but we were so close! Sadly, it was never meant to be. Perhaps it "
                             "was a god, or maybe reality itself rebelled, but the victory that was will never happen. "
                             "Some of us remember it though, if only as a dream.\"",
                 uses=1,
                 cost="200l",
                 function=folded_world):
        Artifact.__init__(self, name, description, uses, cost, function)

    def use(self, *args):
        if self.uses > 0:
            self.uses -= 1
            return self.function(*args)
        else:
            return "What shard? You don't remember any shard."
