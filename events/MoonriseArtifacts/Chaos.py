from events.MoonriseArtifacts.Artifact import Artifact, load_status, update_status
from events.MoonriseCreatures.DarkForestCreature import DarkForestCreature


def creation(target: DarkForestCreature):
    """
    Swaps the current attacker for a random one
    :param target:
    :return:
    """

    data = load_status()
    data['artifact_effects'].append('creation')
    update_status(data)

    return "The pulsing colors of the eye slow, then stop. For a moment, it appears to be looking directly at" \
           " you. Then, you realize the truth. ALL of its eyes are looking at you. The hundreds of eyes " \
           "collapse into one, and when you look at the attacker, it too has changed."


class Chaos(Artifact):
    def __init__(self,
                 name="Encolblanka's 403rd Eye",
                 description='The pupil of this eye is a swirling vortex of colors, slowly fading from one hue into '
                             'the next. "Encolblanka was a god of chaos. It was misconstrued as evil, and its temples '
                             'were ransacked and its followers killed. Not normally a problem for a chaos god, '
                             'but this one happened to love its followers like family. It committed deicide soon '
                             'after."',
                 uses=1,
                 cost="250l",
                 function=creation):
        Artifact.__init__(self, name, description, uses, cost, function)

    def use(self, *args):
        if self.uses > 0:
            self.uses -= 1
            return self.function(*args)
        else:
            return "The eye has turned black as night. No colors swirl in the eye."
