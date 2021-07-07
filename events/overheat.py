import random
import time

import utils.helper_functions as hf

settings = hf.settings
event_settings = settings["events"]
queued_crits = 0

# explosions
explosions = event_settings["explosions"]

# threshold values
shield_threshold = event_settings["shield_threshold"]
safety_threshold = event_settings["safety_threshold"]
explosion_threshold = event_settings["explosion_threshold"]
multiplication_threshold = event_settings["multiplication_threshold"]

# number of seconds to multiply by
time_multiplier = event_settings["time_multiplier"]

# attack values
min_range = event_settings["min_range"]
max_range = event_settings["max_range"]

# crits
crits = event_settings["crits"]
base_critical_chance = event_settings["crit_chance"]
crit_destruction = event_settings["crit_destruction"]

next_attack = time.time()

def overheat():
    global next_attack
    global queued_crits
    shields = hf.get_shield_count()
    attack_damage = random.randint(min_range, max_range)  # randomly generate how much to damage the target by
    adjusted_attack_damage = attack_damage - shields
    output = ""

    if time.time() > next_attack:
        time_delay = adjusted_attack_damage * time_multiplier
        next_attack = time.time() + time_delay
        if crits:
            crit = random.randint(0, 100)

            if queued_crits:
                crit = crit - 20 # this increases the chance of a crit by 20%
                queued_crits = queued_crits - 1
        else:
            crit = 101

        if adjusted_attack_damage > 0:
            output += feed(adjusted_attack_damage, crit < base_critical_chance)

        creation_fluff = ["Flames scorch the ground around the central bonfire as a twisted " +
                          "tree emerges from it, curling protectively around the Campgrounds.",
                          "Another shield tree ascends, its branches meshing with the ones already around it.",
                          "The Salamander hisses as the purple flames are hidden deeper inside the branches of another "
                          "shield tree."]
        if explosions:
            if shield_threshold + safety_threshold < hf.get_campfire_count() < \
                    ((explosion_threshold - hf.get_shield_count()) + safety_threshold):

                hf.set_campfire_count(hf.get_campfire_count() - shield_threshold)
                hf.set_shield_count(hf.get_shield_count()+1)
                output += random.choice(creation_fluff)

            # if explosions are turned on
            elif hf.get_campfire_count() >= ((explosion_threshold - hf.get_shield_count()) + safety_threshold):
                blast_size = hf.get_campfire_count()/2
                blast_damage = int(blast_size/200)
                if blast_damage >= hf.get_shield_count():
                    blast_damage = hf.get_shield_count()

                explosion_fluff = ["The Salamander hisses and begins to glow white-hot. "
                                   "The sparks crackle from its spines as a massive explosion ripples"
                                   " out from the Campgrounds. "+str(blast_damage)+" shields were lost in the blast.",
                                   "A blast of heat ripples across the Campgrounds, followed by a much "
                                   "stronger blast of flame. "+str(blast_damage)+" shields were lost in the damage.",
                                   "A pulse of flame ignites several of the trees around the Campfire. The Salamander "
                                   "giggles maliciously, all kindness has left its eyes. " + str(blast_damage) +
                                   " shield trees were lost in"
                                   "the blast."]

                output =+ random.choice(explosion_fluff)
                hf.set_shield_count(hf.get_shield_count() - blast_damage)
                hf.set_campfire_count(int(hf.get_campfire_count()*0.25))
                queued_crits = queued_crits + blast_damage

        else:
            if safety_threshold < hf.get_campfire_count() - shield_threshold:

                hf.set_campfire_count(hf.get_campfire_count() - shield_threshold)
                hf.set_shield_count(hf.get_shield_count()+1)

                output += random.choice(creation_fluff)
    return output


def feed(reduce_by: int, is_crit: bool):
    retVal = ''
    if event_settings["overheat_active"]:
        interval = 10  # for every 10 past threshold, increase the multiplier by 1
        total_attack = reduce_by

        if is_crit:
            total_attack = total_attack * 4

        vote_data = hf.get_vote_data()
        vote_options = vote_data["Profiles"][hf.get_active_profile()].keys()

        # builds a list of selection choices based off how over the threshold a vote option is
        choices = list(vote_options)

        # add multiple copies of choices with higher values
        for option in vote_options:
            # add at least one copy to the list
            vote_value = hf.get_vote_option_value(option)

            if vote_value >= (multiplication_threshold + interval):
                multiplier = int((hf.get_vote_option_value(option) - multiplication_threshold) / interval)

                for i in range(multiplier):
                    choices.append(option)
        if choices:
            choice = random.choice(choices)
        else:
            return "There are no more stories left in the Campgrounds."

        # make sure it has enough logs to reduce by that much
        if total_attack > hf.get_vote_option_value(choice):
            # if a crit occurs, delete the vote option entirely
            if is_crit:
                crit_consume_fluff = ["The flames of the Campgrounds voraciously devour on %s's log pile. " \
                                      "When it is done, nothing remains. The story has been consumed entirely." % choice,
                                      "A pillar of flame lances from the center of the Campgrounds to %s's logpile. "
                                      "When it is done, not a single splinter remains of the story." % choice,
                                      "The eyes of the Salamander travel to %s's logpile. "
                                      "Seconds later, vines of lilac fire blossom"
                                      " forth and enshroud the story. When the smoke clears, nothing remains." % choice
                                      ]
                retVal += random.choice(crit_consume_fluff)
                hf.set_campfire_count(hf.get_campfire_count() + hf.get_vote_option_value(choice))
                hf.delete_vote_option(choice, hf.get_active_profile())

            else:
                failure_fluff = [f'The questing tendrils of salamander flame pass up '
                                 f'{choice}; It is too small to sate it\'s appetite.']
                retVal += random.choice(failure_fluff)

        else:
            new_value = hf.get_vote_option_value(choice) - total_attack
            if is_crit:
                feed_fluff = [f"Purple fire sprouts from the campfire and sweeps between the other fires, eventually "
                              f"landing on the fire of {choice}. The pillar of flame rages and incinerates {total_attack} "
                              "logs from the that fire.",
                              f"Fire arches from the central campfire and dives onto {choice}"
                              f". {total_attack} logs are consumed."
                              ]
                retVal += random.choice(feed_fluff)
            else:
                retVal += f'The salamander flame gorges itself on {choice}\'s log pile, consuming ' + \
                          str(total_attack) + ' logs. It is sated... for now.'

            # Write the reduced log count to the file.
            hf.set_vote_option_value(choice, new_value)

            hf.set_campfire_count(hf.get_campfire_count() + total_attack)
    return retVal
