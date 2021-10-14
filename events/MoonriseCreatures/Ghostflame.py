from events.MoonriseCreatures.DarkForestCreature import DarkForestCreature


class Ghostflame(DarkForestCreature):

    def __init__(self, delay=300, delayMulti=1.0, attack=0, attackMulti=1.0, health=1000, reward=0, name='Ghostflame'):
        DarkForestCreature.__init__(self, delay, delayMulti, attack, attackMulti, health, reward,
                                    name=name)

    def getAttack(self):
        retval = 'Heedless of all attacks, the ghostly flame simply floats into the fire and merges with it. The ' \
                 'Salamander cries out as it blazes brightly for a few seconds.'
        return retval

    def getCampfireAttack(self):
        retval = 'Heedless of all attacks, the ghostly flame simply floats into the fire and merges with it. The ' \
                 'Salamander cries out as it blazes brightly for a few seconds.'
        return retval

    def getSpawnMessage(self):
        retval = 'The chaos from the eye shoots out, then takes on a life of its own. A being made of viscous fire ' \
                 'floats in the air where the attacker once was, before it slowly starts to move towareds the' \
                 ' Salamander.'
        return retval