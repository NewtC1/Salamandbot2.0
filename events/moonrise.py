import random
import logging
import json
from time import time

from utils import helper_functions as hf
from events.MoonriseCreatures import Dragon, Beast, Colossus, Spider, Ashvine, Bunny, Thunderjaw, Imp, \
    SpiderQueen, Goose, Bonewheel
from events.MoonriseArtifacts.Artifact import load_status, update_status
from events.MoonriseArtifacts.Tusk import Tusk
from events.MoonriseArtifacts.Diamond import Diamond
from events.MoonriseArtifacts.Blowhole import Blowhole
from events.MoonriseArtifacts.Eye import Eye
from events.MoonriseArtifacts.Finger import Finger
from events.MoonriseArtifacts.Heart import Heart
from events.MoonriseArtifacts.Tailbone import Tailbone
from events.MoonriseArtifacts.Tooth import Tooth
from events.MoonriseArtifacts.Scale import Scale


moonrise_status_dir = hf.settings["directories"]["moonrise_status"]


class MoonriseException(Exception):
    pass


class NoUserArtifactError(MoonriseException):
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message


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
        # cicero ability
        self.cicero_buy_order_remaining = hf.settings["events"]["cicero_buy_order_max"]
        self.cicero_time_heart_remaining = hf.settings["events"]["cicero_time_heart_max"]
        self.current_artifact_for_sale = self.spawn_artifact() # spawn a random artifact
        # self.current_artifact_for_sale = Scale()

        self.pending_imp_results = []
        self.imp_no_answer = 0
        self.imp_cooldown = False
        # Set the baseline attacker
        # self.current_attacker = Imp.Imp()
        self.current_attacker = Spider.Spider()
        # set start values
        self.previous_time = time()
        # attackers
        self.attacker_dead = False

        # combo counter
        self.combo_counter = 1.0
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
            soil_off_cooldown = (self.soil_went_on_cooldown + self.soil_cooldown_duration) - time()
            logging.info(f"[Moonrise] Time until Soil comes off Cooldown: {soil_off_cooldown}")

            if soil_off_cooldown < 0:
                self.soil_on_cooldown = False
                logging.info("[Moonrise] Soil coming off cooldown")
                # Parent.SetOBSSourceRender("Soil Ready", True, "Capture", callback)
                set_soil_ready(True)

        if self.bjorn_on_cooldown:
            bjorn_off_cooldown = (self.bjorn_went_on_cooldown + self.bjorn_cooldown_duration) - time()
            logging.info(f"[Moonrise] Time until Bjorn comes off Cooldown: {bjorn_off_cooldown}")
            if bjorn_off_cooldown < 0:
                self.bjorn_on_cooldown = False
                logging.info("[Moonrise] Bjorn coming off cooldown")
                # Parent.SetOBSSourceRender("Bjorn Ready", True, "Capture", callback)
                set_bjorn_ready(True)

        logging.info(f"[Moonrise] Time until the next attack: {self.delay - (time() - self.previous_time)}")
        if int(time() - self.previous_time) > self.delay:
            # spawn a new attacker if dead
            if self.attacker_dead:
                retval = self.set_new_attacker(self.spawn_attacker()) + " "
                self.previous_time = time()
                self.delay = self.current_attacker.get_base_attack_delay() * self.current_attacker.get_attack_delay_multi()
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
                self.delay = self.current_attacker.get_base_attack_delay() * self.current_attacker.get_attack_delay_multi()

        return return_value

    # ----------------------------------------
    # Helper functions
    # ----------------------------------------
    def attack(self):

        retval = ''
        # deal damage to shields are there are still any remaining
        damage = int(self.current_attacker.get_base_attack_atrength() * self.current_attacker.getAttackStrengthMulti())
        if hf.get_shield_count() > 0:
            retval += self.do_damage(damage, retval)
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

    def do_damage(self, damage, retval):
        # increase the shield damage
        status = load_status()
        if status["slaying"]:
            retval += "The creature attempts to attack but suddenly finds itself flopped over on its side, appendages" \
                      " kicking in the air."
            status["slaying"] = False
            update_status(status)
        else:
            hf.set_shield_damage(hf.get_shield_damage() + damage)
            retval += self.current_attacker.getAttack()

        if hf.get_shield_damage() >= self.shield_health:
            # reduce the number of shields if damage hit a health threshold
            hf.set_shield_count(hf.get_shield_count() - 1)
            # reset the shield damage value to 0
            hf.set_shield_damage(0)

            retval += f' The shield shudders and falls, splintering across the ground. ' \
                      f'There are now {hf.get_shield_count()} shields left.'
            self.combo_counter = 1.0
            # resets the supporting abilities.
            self.soil_kill_order_remaining = 1
            self.bjorn_splinter_order_remaining = 3
            self.soil_on_cooldown = False
            self.bjorn_on_cooldown = False
            self.cicero_buy_order_remaining = 1
            self.current_artifact_for_sale = self.spawn_artifact()
            set_soil_ready(True)
            set_soil_kill(True)
            set_bjorn_ready(True)
            set_bjorn_splinter(True)

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
                    scope.delay = scope.kill_attacker()
                    campfire_attack_retval += " The attacker has been slain. You gain " + str(scope.delay) + \
                                              " more seconds until the next attack."
                    campfire_attack_retval += f' Combo counter is at {scope.combo_counter}'
                    logging.info(f'[Moonrise] Combo counter is at {scope.combo_counter}')
                else:
                    scope.current_attacker.SetIncResist(inc_resist - 1)
                    if not str(scope.current_attacker.__class__.__name__).lower() == "imp":
                        campfire_attack_retval += ' Vicious flames curl around the attacker, but fail to dissuade it.' \
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
            # sometimes the system doesn't calculate accurately, so we need to round to 1 digit.
            self.combo_counter = round(self.combo_counter, 1)

        if self.current_attacker.__class__.__name__.lower() == "imp":
            self.imp_cooldown = True
        else:
            self.imp_cooldown = False
        reward = round(self.current_attacker.getReward() * self.combo_counter, 1)
        self.attacker_dead = True

        logging.info(
            f"[Moonrise] Killing attacker {self.current_attacker.name}, gaining {reward}"
            f" seconds before next attack.")

        return reward

    # what happens if the fire goes out?
    def enact_failure(self):
        return "The Salamander's light begins to die, and Soil rushes forward. Plants obliterate the attacker, but it" \
               " is too late. " \
               "Soil erupts into purple flames, then the fire darkens, sucking in light from around her. " \
               "As the the Campgrounds dims, a new light rises from the previously bright bonfire. Moonflowers" \
               " erupt from the firepit and the fire around Soil's unmoving form continues to change, now " \
               "reflecting the new light. " \
               "The light of a goddess. " \
               " With a strangled cry, Soil finally moves, but when she does she leaves some intangible existence " \
               "behind. Her horns lengthen, becoming a full crescent moon, and catch the lunar glow. " \
               "Soraviel, goddess of death, rebirth and change has taken the stage."

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
            if roll < 10:
                return Goose.Goose()
            elif roll < 20:
                return self.spawn_imp()
            elif roll < 30:
                return Bonewheel.Bonewheel()
            elif roll < 50:
                return Spider.Spider()
            elif roll < 80:
                return Beast.Beast()
            else:
                return Colossus.Colossus()
        elif self.get_combo_counter() < 1.4:
            if roll < 10:
                return Goose.Goose()
            elif roll < 30:
                return Spider.Spider()
            elif roll < 40:
                return Beast.Beast()
            elif roll < 80:
                return Colossus.Colossus()
            elif roll < 85:
                return Dragon.Dragon()
            else:
                return Thunderjaw.Thunderjaw()
        elif self.get_combo_counter() < 1.8:
            if roll < 5:
                return Bonewheel.Bonewheel()
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
        else:  # boss encounters
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
            self.delay = self.kill_attacker()
            retval = "As the creature approaches, a mysterious force hits it. It goes sprawling back into the Forest," \
                     " meeting its end on a protruding tree root."

        if phrase.lower() == "aggression":
            hf.set_campfire_count(hf.get_campfire_count() - 100)
            retval = "As you watch, the campfire blazes with a sudden ferocity. Rather than the usual blast of flame, " \
                     "it simply burns through another hundred logs."

        if phrase.lower() == "growth":
            self.current_attacker.setHealth(self.current_attacker.getHealth() * 2)
            self.current_attacker.set_attack_strength_multi(self.current_attacker.getAttackStrengthMulti() * 2)
            self.current_attacker.setAttackDelayMulti(self.current_attacker.get_attack_delay_multi() / 2)
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

    def spawn_imp(self):
        # if not self.imp_cooldown:
        #     pass
            # return Imp.Imp()
        # else:
        self.imp_cooldown = False
        return Bunny.Bunny()

    def spawn_artifact(self):

        roll = random.randint(1,100)
        common = [Tusk, Diamond, Eye, Tooth, Tailbone]
        uncommon = [Finger, Scale]
        rare = [Blowhole]
        legendary = [Heart]

        if roll < 40:
            return random.choice(common)()
        elif roll < 70:
            return random.choice(uncommon)()
        elif roll < 90:
            return random.choice(rare)()
        elif roll < 100:
            return random.choice(legendary)()

    # ========================================= Character Abilities ====================================================

    def soil_restore(self):
        if not self.soil_on_cooldown:
            if hf.get_shield_damage() <= 0:
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

            if self.current_attacker.GetIncResist() > 0:
                roll = random.randint(0,1)
                if roll == 1:
                    self.delay = self.kill_attacker()
                    self.soil_kill_order_remaining -= 1
                    self.soil_went_on_cooldown = time()
                    self.soil_on_cooldown = True
                    set_soil_ready(False)
                    if self.soil_kill_order_remaining == 0:
                        set_soil_kill(False)
                    return "Soil grins and plants a hoof on the ground. Vines, roots and flowers erupt from the " \
                           "ground and strangle, impale and dowse the attacker. Her work done, Soil returns to " \
                           "staring at the fire."
                else:
                    self.soil_kill_order_remaining -= 1
                    self.soil_went_on_cooldown = time()
                    self.soil_on_cooldown = True
                    set_soil_ready(False)
                    if self.soil_kill_order_remaining == 0:
                        set_soil_kill(False)
                    return "Soil plants her hoof, and bamboo spears shoot from the ground, only to he halted by " \
                           "the creature's armor. She glances over at you nervously. " \
                           "\"Well that didn't happen last year.\""
            else:
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
            self.delay = self.current_attacker.get_total_attack_delay() * 5
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

    def cicero_buy(self, user_name):
        if self.cicero_buy_order_remaining > 0 and self.current_artifact_for_sale:

            if self.current_artifact_for_sale.get_cost_type() == "l":
                if hf.get_log_count(user_name) >= self.current_artifact_for_sale.get_cost_value():
                    hf.set_log_count(user_name, hf.get_log_count(user_name) -
                                     self.current_artifact_for_sale.get_cost_value())
                else:
                    return "You don't have enough logs to purchase that."

            if self.current_artifact_for_sale.get_cost_type() == "w":
                if hf.get_woodchip_count(user_name) >= self.current_artifact_for_sale.get_cost_value():
                    hf.set_woodchip_count(user_name, hf.get_woodchip_count(user_name) -
                                          self.current_artifact_for_sale.get_cost_value())
                else:
                    return "You don't have enough woodchips to purchase that."

            # users will only get to this line if they are capable of buying the artifact.
            hf.set_user_artifact(user_name, self.current_artifact_for_sale)
            return_value = f"You have purchased {self.current_artifact_for_sale.get_name()}. This will replace your " \
                           f"current artifact. It has {self.current_artifact_for_sale.get_uses()} uses left."
            self.current_artifact_for_sale = None
            return return_value
        else:
            return 'The owlkin shakes his masked head. "Regrettably, I cannot sell at this time."'


    def cicero_sale(self):
        if self.current_artifact_for_sale:
            item = f"{self.current_artifact_for_sale.name}: {self.current_artifact_for_sale.description} " \
                   f"It has {self.current_artifact_for_sale.get_uses()} uses left. It costs " \
                   f"{self.current_artifact_for_sale.get_cost_value()}{self.current_artifact_for_sale.get_cost_type()}."
            return item
        else:
            return '"Please come back later! I\'ll have something for you then!"'

    def cicero_check(self, user_name):
        artifact = hf.get_user_artifact(user_name)
        if artifact:
            item = f"{artifact.name}: {artifact.description}. " \
                   f"It has {artifact.get_uses()} uses remaining."
            return item
        else:
            return "You haven't yet bought an artifact from Cicero yet. Use !cicero sale and !cicero buy to buy one."

    def cicero_use(self, user_name):
        artifact = hf.get_user_artifact(user_name)
        if hf.get_user_artifact_uses(user_name) > 0:
            hf.set_user_artifact_uses(user_name, hf.get_user_artifact_uses(user_name) - 1)
        return artifact.use(self.current_attacker)

# ================================================== UI functions ======================================================

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


def set_soil_kill(visibility: bool):
    with open(moonrise_status_dir, encoding="utf-8-sig", mode="r") as f:
        data = json.load(f)

    data["soil_kill"] = visibility

    with open(moonrise_status_dir, encoding="utf-8-sig", mode="w") as f:
        json.dump(data, f)