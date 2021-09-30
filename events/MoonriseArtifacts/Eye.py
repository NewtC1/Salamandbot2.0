from events.MoonriseArtifacts.Artifact import Artifact
from events.MoonriseCreatures.DarkForestCreature import DarkForestCreature


def double_value(target: DarkForestCreature):
    target.setReward(target.getReward()*2)
    return "The eye flashes, and the gold flows outward from the pupil, covering the ocular organ."


class Eye(Artifact):
    def __init__(self,
                 name="Jack's Other Eye",
                 description="This eye is the size of a baseball, The iris gleams a purple-gold brilliance. As "
                             "you stare at it, the eye slowly rolls in your hand to look at you.",
                 uses=1,
                 cost="50l",
                 function=double_value):
        Artifact.__init__(self, name, description, uses, cost, function)

    def use(self, *args):
        if self.uses > 0:
            self.uses -= 1
            return self.function(*args)
        else:
            return "The eye has become solid gold, making it extremely heavy."
