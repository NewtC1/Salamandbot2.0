from events.MoonriseCreatures.DarkForestCreature import DarkForestCreature


class Goose(DarkForestCreature):

    def __init__(self, delay=3, delayMulti=1.0, attack=5, attackMulti=1.0, health=100, reward=300):
        DarkForestCreature.__init__(self, delay, delayMulti, attack, attackMulti, health, reward)

    def getAttack(self):
        retval = 'The Goose swings its knife haphazardly at the wooden wall, honking as it does so. Woodchips fly off ' \
                 'as it attempts to bring down a tree with a butterknife.'
        return retval

    def getCampfireAttack(self):
        self.setBaseAttackStrength(1)
        retval = 'The Goose honks at all of those gathered around the fire, flapping its wings majestically. It' \
                 ' charges into the campgrounds and steals a log, then runs out.'
        return retval

    def getSpawnMessage(self):
        retval = 'A HONK breaks the silence as the Goose steps into view, holding a jewel-encrusted butter knife ' \
                 'in its beak.'
        return retval
