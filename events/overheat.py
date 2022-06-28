import logging
import random
import time

import utils.helper_functions as hf


class OverheatManager:

    def __init__(self):
        self.settings = hf.settings
        event_settings = self.settings["events"]
        self.queued_crits = 0

        # explosions
        self.explosions = event_settings["explosions"]

        # threshold values
        self.shield_threshold = event_settings["shield_threshold"]
        self.safety_threshold = event_settings["safety_threshold"]
        self.explosion_threshold = event_settings["explosion_threshold"]
        self.multiplication_threshold = event_settings["multiplication_threshold"]

        # number of seconds to multiply by
        self.time_multiplier = event_settings["time_multiplier"]

        # attack values
        self.min_range = event_settings["min_range"]
        self.max_range = event_settings["max_range"]

        # crits
        self.crits = event_settings["crits"]
        self.base_critical_chance = event_settings["crit_chance"]
        self.crit_destruction = event_settings["crit_destruction"]

    def tick(self):
        output = ""
        if self.settings["events"]["overheat_active"]:
            vote_data = hf.get_vote_data()
            vote_options = list(vote_data["Profiles"][hf.get_active_profile()].keys())
            choices = vote_options.copy()
            interval = 10
            # add multiple copies of choices with higher values
            for option in vote_options:
                # add at least one copy to the list
                vote_value = hf.get_vote_option_value(option)

                if vote_value >= (self.multiplication_threshold + interval):
                    multiplier = int((hf.get_vote_option_value(option) - self.multiplication_threshold) / interval)

                    for i in range(multiplier):
                        choices.append(option)

            choice = random.choice(choices)

            # figure out if we have a crit or not
            critical_chance = self.base_critical_chance if self.queued_crits < 1 else self.base_critical_chance + 100
            self.queued_crits = self.queued_crits-1 if self.queued_crits > 0 else 0
            critical_attack = random.randint(0, 100) < critical_chance

            damage = self.calculate_damage(critical_attack)
            if damage > 0:
                # make sure it has enough logs to reduce by that much
                if damage > hf.get_vote_option_value(choice):
                    # if a crit occurs, delete the vote option entirely
                    if critical_attack:
                        crit_consume_fluff = ["The flames of the Campgrounds voraciously devour on %s's log pile. " \
                                              "When it is done, nothing remains. The story has been consumed entirely." % choice,
                                              "A pillar of flame lances from the center of the Campgrounds to %s's logpile. "
                                              "When it is done, not a single splinter remains of the story." % choice,
                                              "The eyes of the Salamander travel to %s's logpile. "
                                              "Seconds later, vines of lilac fire blossom"
                                              " forth and enshroud the story. When the smoke clears, nothing remains." % choice
                                              ]
                        output += random.choice(crit_consume_fluff)
                        logging.info(f"[Overheat] Destroying {choice} from the vote list: Critical hit deals {damage} to {hf.get_vote_option_value(choice)}")
                        hf.set_campfire_count(hf.get_campfire_count() + hf.get_vote_option_value(choice))
                        hf.delete_vote_option(choice, hf.get_active_profile())
                    else:
                        logging.info(f"[Overheat] Ignoring {choice} from the vote list: {damage} to {hf.get_vote_option_value(choice)}")
                        failure_fluff = [f'The questing tendrils of salamander flame pass up '
                                         f'{choice}; It is too small to sate it\'s appetite.']
                        output += random.choice(failure_fluff)

                else:
                    if critical_attack:
                        feed_fluff = [f"Purple fire sprouts from the campfire and sweeps between the other fires, eventually "
                                      f"landing on the fire of {choice}. The pillar of flame rages and incinerates {damage} "
                                      "logs from the that fire.",
                                      f"Fire arches from the central campfire and dives onto {choice}"
                                      f". {damage} logs are consumed."
                                      ]
                        output += random.choice(feed_fluff)
                    else:
                        output += f'The salamander flame gorges itself on {choice}\'s log pile, consuming ' + \
                                  f'{damage} logs. It is sated... for now.'

                    new_value = hf.get_vote_option_value(choice) - damage
                    logging.info(f"[Overheat] Damaging {choice} from the vote list: {damage} to {hf.get_vote_option_value(choice)}")
                    # Write the reduced log count to the file.
                    hf.set_vote_option_value(choice, new_value)

                    hf.set_campfire_count(hf.get_campfire_count() + damage)
                    hf.set_explosion_damage(hf.get_explosion_damage() + damage*2)
                output += self.resolve_post_attack()
            else:
                output = "The Salamander's attack bashes against the shields, but can't break through the fire-resistant plants."

            return output

    def calculate_damage(self, critical: bool = False):
        damage = random.randint(self.min_range, self.max_range) - hf.get_shield_count()

        if critical:
            damage = damage * 4

        return damage

    def resolve_post_attack(self, critical: bool = False):
        """
        Creates a shield if the campfire's value is within that threshold.
        Creates an explosion if it's not.
        :param critical:
        :return:
        """
        campfire_count = hf.get_campfire_count()
        output = ""

        if campfire_count > self.explosion_threshold - hf.get_shield_count() + self.safety_threshold and self.explosions:
            # generate an explosion
            blast_size = hf.get_explosion_damage()/self.shield_threshold
            blast_damage = int(blast_size)
            if blast_damage >= hf.get_shield_count():
                blast_damage = hf.get_shield_count()

            explosion_fluff = [" The Salamander hisses and begins to glow white-hot. "
                               "The sparks crackle from its spines as a massive explosion ripples"
                               " out from the Campgrounds. "+str(blast_damage)+" shields were lost in the blast.",
                               " A blast of heat ripples across the Campgrounds, followed by a much "
                               "stronger blast of flame. "+str(blast_damage)+" shields were lost in the damage.",
                               " A pulse of flame ignites several of the trees around the Campfire. The Salamander "
                               "giggles maliciously, all kindness has left its eyes. " + str(blast_damage) +
                               " shield trees were lost in"
                               " the blast."]
            logging.info(f"[Overheat] Generating an explosion. Damage: {blast_damage}")
            output += random.choice(explosion_fluff)
            hf.set_explosion_damage(0)
            hf.set_shield_count(hf.get_shield_count() - blast_damage)
            hf.set_campfire_count(int(hf.get_campfire_count()*0.25))
            logging.info(f"[Overheat] Increasing the queued crits by {blast_damage}")
            self.queued_crits = self.queued_crits + blast_damage + 1

        elif campfire_count > self.shield_threshold + self.safety_threshold:
            # generate a shield.

            creation_fluff = ["Flames scorch the ground around the central bonfire as a twisted " +
                              "tree emerges from it, curling protectively around the Campgrounds.",
                              "Another shield tree ascends, its branches meshing with the ones already around it.",
                              "The Salamander hisses as the purple flames are hidden deeper inside the branches of another "
                              "shield tree."]
            logging.info(f"[Overheat] Generating a shield.")
            hf.set_campfire_count(hf.get_campfire_count() - self.shield_threshold)
            hf.set_shield_count(hf.get_shield_count()+1)
            output += random.choice(creation_fluff)

        return output
