from events.MoonriseCreatures.DarkForestCreature import DarkForestCreature

"""Beast(120, 1.0, 70, 1.0, 100, 300)"""  # dpm of 35, increases over time


class Beast(DarkForestCreature):

    def __init__(self, delay=120, delayMulti=1.0, attack=70, attackMulti=1.0, health=100, reward=300, name='Beast'):
        DarkForestCreature.__init__(self, delay, delayMulti, attack, attackMulti, health, reward, name=name)

    def getAttack(self):
        retval = 'The slavering beast claws at the shield, tearing chunks out of it.'
        return retval

    def getCampfireAttack(self):
        self.set_attack_strength_multi(self.getAttackStrengthMulti() + 0.5)
        retval = 'With a howl of triumph, the beast slashes at the Salamander, knocking logs away from fire.'
        return retval

    def getSpawnMessage(self):
        retval = 'A howl echoes through the forest. An attack is coming.'
        return retval
