from events.MoonriseCreatures.DarkForestCreature import DarkForestCreature


class Vine(DarkForestCreature):

    def __init__(self, delay, delayMulti, attack, attackMulti, health, reward, name='Vine'):
        DarkForestCreature.__init__(self, delay, delayMulti, attack, attackMulti, health, reward, name=name)


    def getAttack(self):
        retval = 'Vines thrash at the barrier, leaving long slashes in the shield\'s thick trunk.'
        return retval

    def getCampfireAttack(self):
        retval = 'Long thorny vines curl around the logs at the edge of the fire, pulling them back into the forest.'
        return retval

    def getSpawnMessage(self):
        retval = 'A soft sliding noise emanates from the depths of the Dark Forest.'
        return retval