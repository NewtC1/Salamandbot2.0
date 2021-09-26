import random
import logging
import json
from time import time

from utils import helper_functions as hf
from events.MoonriseCreatures import Dragon, Beast, Colossus, Spider, Ashvine, Bunny, Thunderjaw, Imp, SpiderQueen

moonrise_status_dir = hf.settings["directories"]["moonrise_status"]


class MoonriseManager:
    def __init__(self, logger: logging.Logger):
        self.logger = logger

        self.delay = hf.settings["events"]["delay"]

        # soil ability cooldowns
        self.soil_kill_order_remaining = hf.settings["events"]["soil_kill_order_max"]
        self.soil_on_cooldown = False
        self.soil_cooldown_duration = hf.settings["events"]["soil_cooldown_duration"]
        self.soil_went_on_cooldown = time() - self.soil_cooldown_duration
        # bjorn ability
        self.bjorn_splinter_order_remaining = hf.settings["events"]["bjorn_splinter_order_max"]
        self.bjorn_on_cooldown = False
        self.bjorn_cooldown_duration = hf.settings["events"]["bjorn_cooldown_duration"]
        self.bjorn_went_on_cooldown = time() - self.bjorn_cooldown_duration

        self.pending_imp_results = []
        self.imp_no_answer = 0
        # Set the baseline attacker
        self.current_attacker = Imp.Imp()
        # set start values
        self.previous_time = time()
        # attackers
        self.attacker_dead = False

        # combo counter
        self.combo_counter = 0
        self.combo_counter_cap = 2.0

        # shields
        self.shield_health = hf.settings["events"]["shield_health"]
        self.campfire_attack_safety_threshold = hf.settings["events"]["campfireAttackSafetyThreshold"]

        set_soil_ready(True)
        set_soil_kill(True)
        set_bjorn_ready(True)
        set_bjorn_splinter(True)

        return

    def tick(self):
        return_value = ""

        if self.soil_on_cooldown:
            if self.soil_went_on_cooldown + self.soil_cooldown_duration < time():
                self.soil_on_cooldown = False
                logging.info("[Moonrise] Soil coming off cooldown")
                # Parent.SetOBSSourceRender("Soil Ready", True, "Capture", callback)
                set_soil_ready(True)

        if self.bjorn_on_cooldown:
            if self.bjorn_went_on_cooldown + self.bjorn_cooldown_duration < time():
                self.bjorn_on_cooldown = False
                logging.info("[Moonrise] Bjorn coming off cooldown")
                # Parent.SetOBSSourceRender("Bjorn Ready", True, "Capture", callback)
                set_bjorn_ready(True)

        # logging.info(f"[Moonrise] Time until the next attack: {self.delay - (time()-self.previous_time)}")
        if int(time() - self.previous_time) > self.delay:
            # spawn a new attacker if dead
            if self.attacker_dead:
                retval = self.set_new_attacker(self.spawn_attacker()) + " "
                self.previous_time = time()
                # if the attacker is not an imp, go through the list of imp rewards and clear it.
                if str(self.current_attacker.__class__.__name__).lower() != "imp":
                    for phrase in self.pending_imp_results:
                        retval += self.resolve_imp_phrase(phrase) + " "
                    self.pending_imp_results = []
                return retval
            else:
                # do an attack action
                return_value += self.attack()
                self.previous_time = time()

            if not self.attacker_dead:
                self.delay = self.current_attacker.getBaseAttackDelay() * self.current_attacker.getAttackDelayMulti()

        return return_value

    # ----------------------------------------
    # Helper functions
    # ----------------------------------------
    def attack(self):

        retval = ''
        shield_amount = hf.get_shield_count()
        # deal damage to shields are there are still any remaining
        damage = int(self.current_attacker.getBaseAttackStrength() * self.current_attacker.getAttackStrengthMulti())
        if shield_amount > 0:
            retval += self.do_damage(damage, retval, shield_amount)
        else:
            # read the value
            campfire_value = hf.get_campfire_count()
            campfire_value = int(campfire_value - damage)
            # open and save the new damage
            hf.set_campfire_count(campfire_value)

            retval += self.current_attacker.getCampfireAttack()

            # if the campfire isn't at 0, counter attack
            if campfire_value > 0:
                retval += self.counter_attack(retval)
            # else, begin the fail state
            else:
                self.enact_failure()

        return retval

    def do_damage(self, damage, retval, shield_amount):
        # open the current shield damage file
        shield_damage = hf.get_shield_damage()
        # increase the shield damage
        shield_damage += damage
        retval += self.current_attacker.getAttack()

        if shield_damage >= self.shield_health:
            # reduce the number of shields if damage hit a health threshold
            shield_amount = shield_amount - 1
            # reset the shield damage value to 0
            shield_damage = 0

            # respond('Just before the write')
            hf.set_shield_damage(shield_damage)
            retval += ' The shield shudders and falls, splintering across the ground. There are now ' + str(
                shield_amount) + ' shields left.'
            self.combo_counter = 1.0
            # resets the supporting abilities.
            self.soil_kill_order_remaining = 1
            self.bjorn_splinter_order_remaining = 3
            self.soil_on_cooldown = False
            self.bjorn_on_cooldown = False
            set_soil_ready(True)
            set_soil_kill(True)
            set_bjorn_ready(True)
            set_bjorn_splinter(True)

        # open and save the new damage
        hf.set_shield_damage(shield_damage)

        # respond('Successful write completed. Moving to counterattack.')

        return self.counter_attack(retval)

    def counter_attack(self, output):
        # Parent.SendStreamMessage("Starting counter attack")
        retval = output

        # The the salamander counter attacks if it has the logs to beat the current attacker.
        campfire = hf.get_campfire_count()

        inc_resist = self.current_attacker.GetIncResist()

        # respond(str(campfire >= current_attacker.getHealth()))
        if campfire >= self.current_attacker.getHealth():
            # read the value
            shield_amount = hf.get_shield_count()

            def imp_response(scope):

                retval = ""
                # respond(str(1 <= self.imp_no_answer < 3))
                if scope.imp_no_answer < 1:
                    scope.imp_no_answer += 1
                elif 1 <= scope.imp_no_answer < 3:
                    retval += ' The imp stomps its foot. "That\'s %i times you\'ve avoided answering.' \
                              ' At 3 I\'ll get angry.' % scope.imp_no_answer
                    scope.imp_no_answer += 1
                elif scope.imp_no_answer >= 3:
                    retval += ' The imp disappears with a howl of rage. "You were warned, and now you\'ll pay! ' \
                              'Let today be your judgement day!"'
                    result = scope.current_attacker.check_answer("No answer")
                    scope.pending_imp_results.append(result)
                    scope.delay = scope.kill_attacker()
                    scope.imp_no_answer = 0
                return retval

            def resolve_campfire_attack(scope):
                campfire_attack_retval = ""
                if inc_resist < 1:
                    campfire_attack_retval += ' Flame roars from the Campfire, incinerating the attacker instantly.'
                    hf.set_campfire_count(hf.get_campfire_count() - scope.current_attacker.getHealth())
                    # open and save the new damage
                    delay = scope.kill_attacker()
                    campfire_attack_retval += " The attacker has been slain. You gain " + str(delay) + \
                                              " more seconds until the next attack."
                    campfire_attack_retval += ' Combo counter is at ' + str(self.combo_counter)
                    logging.info('[Moonrise] Combo counter is at ' + str(self.combo_counter))
                else:
                    scope.current_attacker.SetIncResist(inc_resist - 1)
                    if not str(scope.current_attacker.__class__.__name__).lower() == "imp":
                        campfire_attack_retval += ' Vicious flames curl around the attacker, but fail to disuade it.' \
                                  ' Burns race across the creature\'s body.'
                        campfire_attack_retval += scope.current_attacker.UseSpecialAbility()
                    else:
                        campfire_attack_retval += imp_response(scope)

                return campfire_attack_retval

            # The the salamander counter attacks if it has the logs to beat the current attacker.
            if shield_amount > 0:
                if (self.current_attacker.getHealth() + self.campfire_attack_safety_threshold) <= campfire:
                    retval += resolve_campfire_attack(self)
            # if there are no shields left, ignore the safety threshold
            else:
                if self.current_attacker.getHealth() < campfire:
                    retval += resolve_campfire_attack(self)

        return retval

    # sets the values of the new attacker
    def set_new_attacker(self, attacker):
        logging.info(f"[Moonrise] Setting a new attacker: {attacker.__class__.__name__}")
        self.current_attacker = attacker
        self.attacker_dead = False
        return attacker.getSpawnMessage()

    def kill_attacker(self):
        if self.combo_counter < self.combo_counter_cap:
            self.combo_counter += 0.1

        reward = self.current_attacker.getReward()
        self.attacker_dead = True

        logging.info(
            f"[Moonrise] Killing attacker {self.current_attacker.name}, gaining {reward*self.combo_counter}"
            f" seconds before next attack.")

        return reward

    # what happens if the fire goes out?
    def enact_failure(self):
        return """
                With a last gasp, the central bonfire consumes all of the remaining logs in the entire Campgrounds and fizzles out.
                In darkness, a pregnant silence falls. 
                One second. Two seconds. 
                Then Soil screams. 
                Moonflowers erupt from the ashes, then the dirt around the ashes. 
                In seconds, the darkness is obliterated by death's light. 
                The space around Soil ripples. 
                A silver orb shines between her horns, and a kopesh of moonlight is embraced in her hands. 
                Soraviel, Moon Goddess of Death and Rebirth, makes her presence known. 
                """

    def spawn_attacker(self):
        """
        attackers = [Spider(),  # dpm of 15
                     ShadowBoundBear(),  # dpm of 30
                     Beast(),  # dpm of 35, increases over time
                     Colossus(),  # dpm of 140, increases over time
                     Dragon(),  # dpm of 200. Reward increases over time, difficult to kill.
                     Ashvine(),  # dpm of 30. Increases over time, harder to kill over time, reward increases over time.
                     Bunny(),   # unspeakably evil
                     Thunderjaw()]
        """
        roll = random.randint(1, 100)

        if self.get_combo_counter() < 1.2:
            if roll < 20:
                return Imp.Imp()
            elif roll < 50:
                return Spider.Spider()
            elif roll < 80:
                return Beast.Beast()
            elif roll < 90:
                return Colossus.Colossus()
            else:
                return Bunny.Bunny()
        elif self.get_combo_counter() < 1.4:
            if roll < 10:
                return Imp.Imp()
            elif roll < 30:
                return Spider.Spider()
            elif roll < 40:
                return Beast.Beast()
            elif roll < 80:
                return Colossus.Colossus()
            elif roll < 85:
                return Dragon.Dragon()
            elif roll < 90:
                return Thunderjaw.Thunderjaw()
            else:
                return Bunny.Bunny()
        elif self.get_combo_counter() < 1.8:
            if roll < 5:
                return Imp.Imp()
            elif roll < 40:
                return Beast.Beast()
            elif roll < 50:
                return Colossus.Colossus()
            elif roll < 70:
                return Dragon.Dragon()
            elif roll < 90:
                return Thunderjaw.Thunderjaw()
            else:
                return Ashvine.Ashvine()
        elif self.get_combo_counter() < 2.0:
            if roll < 40:
                return Dragon.Dragon()
            elif roll < 90:
                return Thunderjaw.Thunderjaw()
            else:
                return Ashvine.Ashvine()
        else: # boss encounters
            if roll < 50:
                return Ashvine.Ashvine()
            else:
                return SpiderQueen.SpiderQueen()

    def get_combo_counter(self):
        return self.combo_counter

    def resolve_imp_phrase(self, phrase):
        # respond("Resolving " + phrase)

        """
        Possible reward phrases include:
            "aegis" = add shield
            "Yanaviel" = restore
            "Soraviel" = kill creature
            "aggression" = attack
            "growth" = buff creature
            "decay" = splinter creature
            "dragon" = double base reward
        :param phrase:
        :return:
        """
        retval = ""

        if phrase.lower() == "aegis":
            hf.set_shield_count(hf.get_shield_count() + 1)
            retval = "Before your eyes, the damage on the shield tree melts away."

        if phrase.lower() == "yanaviel":
            hf.set_shield_damage("0")
            retval = "Before your eyes, the damage on the shield tree melts away."

        if phrase.lower() == "soraviel":
            delay = self.kill_attacker()
            retval = "As the creature approaches, a mysterious force hits it. It goes sprawling back into the Forest," \
                     " meeting its end on a protruding tree root."

        if phrase.lower() == "aggression":
            hf.set_campfire_count(hf.get_campfire_count() - 100)
            retval = "As you watch, the campfire blazes with a sudden ferocity. Rather than the usual blast of flame, " \
                     "it simply burns through another hundred logs."

        if phrase.lower() == "growth":
            self.current_attacker.setHealth(self.current_attacker.getHealth() * 2)
            self.current_attacker.setAttackStrengthMulti(self.current_attacker.getAttackStrengthMulti() * 2)
            self.current_attacker.setAttackDelayMulti(self.current_attacker.getAttackDelayMulti() / 2)
            retval = "The creature approaches the campfire, but there's something different about this one. " \
                     "It's bigger, meaner, and angrier."

        if phrase.lower() == "decay":
            self.current_attacker.SetIncResist(0)
            retval = "The approaching creature seems diseased. While no weaker, its skin is paper thin, and it sweats a" \
                     " greasy substance."

        if phrase.lower() == "dragon":
            self.current_attacker.setReward(self.current_attacker.getReward() * 2)
            retval = "This creature is no bigger, no weaker, and no more flammable than the rest. But it IS shinier " \
                     "than the rest."

        return retval

    def soil_restore(self):
        if not self.soil_on_cooldown:
            if hf.get_shield_damage() == 0:
                return ('"Nuh-uh chief. Those trees are as green as they get." Soil leans back on her log, '
                        'twirling a glowing moonflower in her hand. "Maybe save my talents for something actually '
                        'threatening? Just a thought."')

            hf.set_shield_damage(0)
            self.soil_went_on_cooldown = time()
            self.soil_on_cooldown = True
            set_soil_ready(False)
            return ("Placing a hand on the nearest damaged shield, Soil convinces life to flow into the tree. "
                    "Sap flows back into the gaping wounds in its bark, and the bark reseals.")
        else:
            return ('"Nope. Can\'t do that too often. Making new life is one thing, but healing? '
                    'I\'m not made for that." Soil looks down at her hooves, lost in thought. '
                    '"What *am* I made for?"')


    def soil_kill(self):
        if self.soil_kill_order_remaining > 0 and not self.soil_on_cooldown:
            if self.attacker_dead:
                return ('"Attack what? There\'s nothing out there." Soil looks at you, clearly doubting your '
                        'sanity.')
            self.delay = self.kill_attacker()
            self.soil_kill_order_remaining -= 1
            self.soil_went_on_cooldown = time()
            self.soil_on_cooldown = True
            set_soil_ready(False)
            if self.soil_kill_order_remaining == 0:
                set_soil_kill(False)
            return ("Soil grins and plants a hoof on the ground. "
                    "Vines, roots and flowers erupt from the ground and strangle, impale and dowse the attacker. "
                    "Her work done, Soil returns to staring at the fire.")
        else:
            return ('"I think we can wait this one out a bit. Let me know when it actually breaks through." Soil '
                    'grins, showing off her sharpened teeth. "What\'s life without a bit of danger?"')

    def bjorn_delay(self):
        if not self.bjorn_on_cooldown:
            if self.attacker_dead:
                return 'Bjorn shrugs. "Nothing out there right now."'
            self.delay = self.delay * 5
            return_value = 'Bjorn once more disappears into the trees, taking his bow and several poisoned arrows. ' \
                           'It\'s hard to track his movements as he disappears into the gloom. A few minutes later ' \
                           'he returns. "That should slow it down for a bit."'
            self.bjorn_on_cooldown = True
            self.bjorn_went_on_cooldown = time()
            set_bjorn_ready(False)
            return return_value
        else:
            return '"Not yet." Bjorn hunkers under his blanket. "The big ones are still coming."'

    def bjorn_splinter(self):
        if self.bjorn_splinter_order_remaining > 0 and not self.bjorn_on_cooldown:
            if self.current_attacker.GetIncResist() == 0:
                return 'Bjorn doesn\'t even bother to move. "No armor, no point."'
            if self.attacker_dead:
                return '"Nothing\'s there yet." Bjorn leans back against the tree he\'s climbed.'
            self.current_attacker.SetIncResist(0)
            self.bjorn_splinter_order_remaining -= 1
            self.bjorn_on_cooldown = True
            self.bjorn_went_on_cooldown = time()
            set_bjorn_ready(False)
            if self.bjorn_splinter_order_remaining == 0:
                set_bjorn_splinter(False)
            return 'Bjorn wordlessly walks from the Campgrounds. Minutes pass. ' \
                            'A scream sounds in the distance. ' \
                            'Bjorn returns. "Job\'s done." He slumps back onto his log.'
        else:
            return 'Bjorn shakes his shaggy head and goes back to sleep.'


def set_bjorn_ready(visibility: bool):
    with open(moonrise_status_dir, encoding="utf-8-sig", mode="r") as f:
        data = json.load(f)

    data["bjorn_ready"] = visibility

    with open(moonrise_status_dir, encoding="utf-8-sig", mode="w") as f:
        json.dump(data, f)


def set_bjorn_splinter(visibility: bool):
    with open(moonrise_status_dir, encoding="utf-8-sig", mode="r") as f:
        data = json.load(f)

    data["bjorn_splinter"] = visibility

    with open(moonrise_status_dir, encoding="utf-8-sig", mode="w") as f:
        json.dump(data, f)


def set_soil_ready(visibility: bool):
    with open(moonrise_status_dir, encoding="utf-8-sig", mode="r") as f:
        data = json.load(f)

    data["soil_ready"] = visibility

    with open(moonrise_status_dir, encoding="utf-8-sig", mode="w") as f:
        json.dump(data, f)


def set_soil_kill(visibility:bool):
    with open(moonrise_status_dir, encoding="utf-8-sig", mode="r") as f:
        data = json.load(f)

    data["soil_kill"] = visibility

    with open(moonrise_status_dir, encoding="utf-8-sig", mode="w") as f:
        json.dump(data, f)