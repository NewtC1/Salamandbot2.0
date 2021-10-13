from utils import helper_functions as hf
from events.MoonriseCreatures.DarkForestCreature import DarkForestCreature


class Bonewheel(DarkForestCreature):

    def __init__(self, delay=400, delayMulti=1.0, attack=200, attackMulti=1.0, health=50, reward=300, name='Skeleton'):
        DarkForestCreature.__init__(self, delay, delayMulti, attack, attackMulti, health, reward, name=name)

    def getAttack(self):
        retval = 'Again, the laughter heralds the arrival of the bonewheel as it grinds a furrow into a trunk. '
        return retval

    def getCampfireAttack(self):
        self.set_attack_strength_multi(self.getAttackStrengthMulti() + 0.5)
        retval = 'The bonewheel sprays even more dirt into the campfire, dousing it down.'
        return retval

    def getSpawnMessage(self):

        if hf.get_shield_count() > 0:
            hf.set_shield_damage(hf.get_shield_damage() + self.get_total_attack_strength())
            retval = 'With a rattling of bones an a gleeful cackle, a skeleton nailed to a wheel zooms into the ' \
                     'Campgrounds. It slams up against the ring of trees and grinds the spiked spokes against it.'
        else:
            hf.set_campfire_count(hf.get_campfire_count() - self.get_total_attack_strength())
            retval = 'Cheerfully spinning in, a bonewheel skeleton whirls out of the Forest depths, throwing dirt ' \
                     'on the fire, then zooms out again.'

        return retval
