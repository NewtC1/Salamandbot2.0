import random
import logging
from time import time

from utils import helper_functions as hf
from MoonriseCreatures import Dragon, Beast, Colossus, Spider, Ashvine, Bunny, Thunderjaw, Imp, SpiderQueen


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

        return

    def tick(self):

        if self.soil_on_cooldown:
            if self.soil_went_on_cooldown + self.soil_cooldown_duration < time():
                self.soil_on_cooldown = False
                # Parent.SetOBSSourceRender("Soil Ready", True, "Capture", callback)

        if self.bjorn_on_cooldown:
            if self.bjorn_went_on_cooldown + self.bjorn_cooldown_duration < time():
                self.bjorn_on_cooldown = False
                # Parent.SetOBSSourceRender("Bjorn Ready", True, "Capture", callback)

        # respond("Time until the next attack: " + str(delay - (time()-previous_time)))
        if int(time() - self.previous_time) > self.delay:
            # spawn a new attacker if dead
            if attacker_dead:
                retval = self.set_new_attacker(self.spawn_attacker()) + " "
                self.previous_time = time()
                # if the attacker is not an imp, go through the list of imp rewards and clear it.
                if str(current_attacker.__class__.__name__).lower() != "imp":
                    for phrase in self.pending_imp_results:
                        retval += self.resolve_imp_phrase(phrase) + " "
                    self.pending_imp_results = []
                return retval
            else:
                # do an attack action
                self.attack()
                self.previous_time = time()

            if not attacker_dead:
                self.delay = current_attacker.getBaseAttackDelay() * current_attacker.getAttackDelayMulti()

    # ----------------------------------------
    # Helper functions
    # ----------------------------------------
    def attack(self):

        retval = ''
        shield_amount = hf.get_shield_count()
        # deal damage to shields are there are still any remaining
        damage = int(current_attacker.getBaseAttackStrength() * current_attacker.getAttackStrengthMulti())
        if shield_amount > 0:
            # open the current shield damage file
            shield_damage = hf.get_shield_damage()
            # increase the shield damage
            shield_damage += damage
            retval += current_attacker.getAttack()

            # respond(shielddamage >= shieldHealth)
            # debug output
            # respond(retval)
            # respond('Shield damage is now at ' + str(shielddamage))
            # if the damage exceeded the current shield health
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
                self.soil_kill_orders_remaining = 1
                self.bjorn_splinter_order_remaining = 3
                self.soil_on_cooldown = False
                self.bjorn_on_cooldown = False
                # Parent.SetOBSSourceRender("Soil Kill", True, "Capture", callback)
                # Parent.SetOBSSourceRender("Soil Ready", True, "Capture", callback)
                # Parent.SetOBSSourceRender("Bjorn Splinter", True, "Capture", callback)
                # Parent.SetOBSSourceRender("Bjorn Ready", True, "Capture", callback)

            # open and save the new damage
            hf.set_shield_damage(shield_damage)

            # respond('Successful write completed. Moving to counterattack.')

            self.counter_attack(retval)

        else:
            # read the value
            campfire_value = hf.get_campfire_count()
            campfire_value = int(campfire_value - damage)
            # open and save the new damage
            hf.set_campfire_count(campfire_value)

            retval += current_attacker.getCampfireAttack()

            # if the campfire isn't at 0, counter attack
            if campfire_value > 0:
                self.counter_attack(retval)
            # else, begin the fail state
            else:
                self.enact_failure()

    def counter_attack(self, output):
        # Parent.SendStreamMessage("Starting counter attack")
        retval = output

        global campfireAttackSafetyThreshold
        global current_attacker
        global combo_counter
        global delay
        global imp_no_answer

        # The the salamander counter attacks if it has the logs to beat the current attacker.
        campfire = hf.get_campfire_count()

        inc_resist = current_attacker.GetIncResist()

        # respond(str(campfire >= current_attacker.getHealth()))
        if campfire >= current_attacker.getHealth():
            # read the value
            shield_amount = hf.get_shield_count()

            def imp_response():
                global imp_no_answer
                global delay

                retval = ""
                # respond(str(1 <= imp_no_answer < 3))
                if imp_no_answer < 1:
                    imp_no_answer += 1
                elif 1 <= imp_no_answer < 3:
                    retval += ' The imp stomps its foot. "That\'s %i times you\'ve avoided answering.' \
                              ' At 3 I\'ll get angry.' % imp_no_answer
                    imp_no_answer += 1
                elif imp_no_answer >= 3:
                    retval += ' The imp disappears with a howl of rage. "You were warned, and now you\'ll pay! ' \
                              'Let today be your judgement day!"'
                    result = current_attacker.check_answer("No answer")
                    super.pending_imp_results.append(result)
                    delay = super.kill_attacker()
                    imp_no_answer = 0
                return retval

            def resolve_campfire_attack():
                global delay
                campfire_attack_retval = ""
                if inc_resist < 1:
                    campfire_attack_retval += ' Flame roars from the Campfire, incinerating the attacker instantly.'
                    hf.set_campfire_count(hf.get_campfire_count() - current_attacker.getHealth())
                    # open and save the new damage
                    delay = super.kill_attacker()
                    campfire_attack_retval += " The attacker has been slain. You gain " + str(delay) + \
                                              " more seconds until the next attack."
                    campfire_attack_retval += ' Combo counter is at ' + str(combo_counter)
                    logging.info('[Moonrise] Combo counter is at ' + str(combo_counter))
                else:
                    current_attacker.SetIncResist(inc_resist - 1)
                    if not str(current_attacker.__class__.__name__).lower() == "imp":
                        campfire_attack_retval += ' Vicious flames curl around the attacker, but fail to disuade it.' \
                                  ' Burns race across the creature\'s body.'
                        campfire_attack_retval += current_attacker.UseSpecialAbility()
                    else:
                        campfire_attack_retval += imp_response()

                return campfire_attack_retval

            # The the salamander counter attacks if it has the logs to beat the current attacker.
            if shield_amount > 0:
                if (current_attacker.getHealth() + campfireAttackSafetyThreshold) <= campfire:
                    retval += resolve_campfire_attack()
            # if there are no shields left, ignore the safety threshold
            else:
                if current_attacker.getHealth() < campfire:
                    retval += resolve_campfire_attack()

        return retval

    # sets the values of the new attacker
    def set_new_attacker(self, attacker):
        global current_attacker
        global attacker_dead
        current_attacker = attacker
        attacker_dead = False
        return attacker.getSpawnMessage()

    def kill_attacker(self):
        # currentAttacker

        if self.combo_counter < self.combo_counter_cap:
            self.combo_counter += 0.1

        reward = current_attacker.getReward()
        self.attacker_dead = True

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
        global combo_counter
        return combo_counter

    def resolve_imp_phrase(self, phrase):
        global delay
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
            current_attacker.setHealth(current_attacker.getHealth() * 2)
            current_attacker.setAttackStrengthMulti(current_attacker.getAttackStrengthMulti() * 2)
            current_attacker.setAttackDelayMulti(current_attacker.getAttackDelayMulti() / 2)
            retval = "The creature approaches the campfire, but there's something different about this one. " \
                     "It's bigger, meaner, and angrier."

        if phrase.lower() == "decay":
            current_attacker.SetIncResist(0)
            retval = "The approaching creature seems diseased. While no weaker, its skin is paper thin, and it sweats a" \
                     " greasy substance."

        if phrase.lower() == "dragon":
            current_attacker.setReward(current_attacker.getReward() * 2)
            retval = "This creature is no bigger, no weaker, and no more flammable than the rest. But it IS shinier " \
                     "than the rest."

        return retval

    # def callback(jsonString):
        # Return the Json String that OBS returns
        # return

    def callback(response):
        """ Logs callback error response in scripts logger. """
        parsedresponse = json.loads(response)
        if parsedresponse["status"] == "error":
            Parent.Log("OBS Remote", parsedresponse["error"])
        return

    def display_source(source, scene):
        Parent.SetOBSSourceRender(source, True, scene, callback)
