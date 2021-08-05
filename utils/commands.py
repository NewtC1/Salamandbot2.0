import os
import toml
import time
import re
import operator
import requests
import data_classes.redeemable as redeemable
from utils import helper_functions as hf
from voting.vote_manager import VoteManager

settings = toml.load(os.path.join(os.path.dirname(__file__), "settings.toml"))


def commands(to_parse=None):
    """

    :param to_parse: None expected
    :return:
    """
    output = f"Commands can be found here: {settings['links']['commands']}"
    return output


def blind(to_parse=None):
    """
    The Blind string.
    :param to_parse: None expected
    :return:
    """
    output = f"No story spoilers, and no advice unless I ask for it."
    return output


def charity(to_parse=None):
    """
    Outputs the link and name of whatever charity I'm supporting at the time.
    :param to_parse: None expected
    :return:
    """
    output = f"We're currently supporting {settings['strings']['charity_name']} at {settings['links']['charity']}"
    return output


def christmas(to_parse=None):
    """
    Returns the christmas blurb
    :param to_parse: None expected
    :return:
    """
    output = settings['events']['rimeheart']
    return output


def discord(to_parse=None):
    """
    Returns the link to the Discord.
    :param to_parse: None expected
    :return:
    """
    output = f"To join the Campgrounds community, you can find us in the Riverbank at {settings['links']['discord']}." \
             f" Make sure to select roles!"
    return output


def encore(to_parse=None):
    """
    Returns the encore event blurb
    :param to_parse: None expected
    :return:
    """
    output = settings['events']['encore']
    return output


def festival(to_parse=None):
    """
    Returns the christmas blurb
    :param to_parse: None expected
    :return:
    """
    output = settings['events']['festival']
    return output


def followage(to_parse=None):
    """
    Returns a string which displays how long the user has been following the stream.
    :param to_parse:
    :return:
    """

    output = f"https://decapi.me/twitch/followed?channel={settings['strings']['channel_name'].lower()}&user={to_parse.author.name}"
    return output


def humble(to_parse=None):
    """
    Displays the Humble Bundle Link
    :param to_parse:
    :return:
    """
    output = f"Humble Bundle link: {settings['links']['humble_bundle']}"
    return output


def info(to_parse=None):
    """
    Displays all info for the stream.
    :param to_parse:
    :return:
    """
    output = "Discord: https://discord.gg/JMPnhBK \n " \
             "Patreon: https://www.patreon.com/NewtC \n " \
             "World Anvil: https://www.worldanvil.com/w/the-dark-forest-newtc \n " \
             "Humble Bundle: https://www.humblebundle.com/?partner=newtc \n " \
             "YouTube: https://www.youtube.com/watch?v=7RNeMl9qLMY&feature=youtu.be"
    return output


def logs(to_parse=None):
    """
    Displays the user's log count
    :param to_parse:
    :return:
    """
    output = f"{to_parse.author.name} has gathered {hf.get_log_count(to_parse.author.name)} logs."
    return output


def lurk(to_parse=None):
    """
    Display a lurk message. Also gives the user a single log if they don't already have one.
    :param to_parse:
    :return:
    """
    output = f"{to_parse.author.name} pulls up a log and sits down to enjoy the stories."

    users = hf.get_user_list()
    author_name = to_parse.author.name

    if author_name in users:
        if hf.get_log_count(author_name) == 0:
            hf.set_log_count(author_name.lower(), 1)
    else:
        hf.set_log_count(author_name.lower(), 1)

    return output


def modlist(to_parse=None):
    """
    Gives a link to the list of Oblivion mods.
    :param to_parse:
    :return:
    """
    output = f"Modlist: {settings['links']['modlist']}"
    return output


def moonrise(to_parse=None):
    """
    Displays the Moonrise text.
    :param to_parse:
    :return:
    """
    output = f"{settings['events']['moonrise']}"
    return output


def overheat(to_parse=None):
    """
    Displays the overheat.py text.
    :param to_parse:
    :return:
    """
    output = f"{settings['events']['overheat']}"
    return output


def patreon(to_parse=None):
    """
    Displays the link to Patreon
    :param to_parse:
    :return:
    """
    output = f"{settings['links']['patreon']}"
    return output


def planttrees(to_parse=None):
    """
    Plants some trees.
    TODO: Makes this do something more significant.
    :param to_parse:
    :return:
    """
    output = f"{settings['strings']['plant_trees']}"
    return output


def pobox(to_parse=None):
    """
    Returns the mailing address for the PO box
    :param to_parse:
    :return:
    """
    output = "You can send stuff to me at the following address: \n" \
             "7241 185th Ave NE \n" \
             "# 2243 \n" \
             "Redmond, WA 98073"
    return output


def prizechoice(to_parse=None):
    """
    Returns the list of prizes users can choose from for Rimeheart
    :param to_parse:
    :return:
    """
    output = f"{settings['strings']['prize_choice']}"
    return output


def shoutout(to_parse=None):
    """
    Shouts out the given user.
    :param to_parse:
    :return:
    """
    target_channel = to_parse.content.split()[1]

    if target_channel[0] == "@":
        target_channel = target_channel[1:]

    headers = {
        'client-id': hf.client_id,
        'Authorization': f'Bearer {hf.irc_token}'
    }

    target_user = requests.get(f"https://api.twitch.tv/helix/users?login={target_channel}", headers=headers).json()['data'][0]['id']
    response = requests.get(f"https://api.twitch.tv/helix/channels?broadcaster_id={target_user}", headers=headers).json()
    user = response["data"][0]["broadcaster_name"]
    game = response["data"][0]["game_name"]
    user_login = response["data"][0]["broadcaster_login"]
    output = f"{user} is a friend of the Campgrounds. Last they were seen, they were telling the story of " \
             f"{game}. Check them out at https://www.twitch.tv/{user_login}"

    return output


def so(to_parse=None):
    return shoutout(to_parse)


def top5(to_parse=None):
    output = ""

    accounts = hf.load_accounts()
    log_counts = {}
    for account in accounts:
        log_counts[accounts[account]["active_name"]] = accounts[account]["logs"]

    sorted_log_count = reversed(sorted(log_counts.items(), key=lambda kv: kv[1]))
    count = 1

    for k, v in sorted_log_count:
        output += f"{count}: {k}({v})"
        count += 1

        if count == 6:
            break
        else:
            output += ", "

    return output


def worldanvil(to_parse=None):
    """
    REturns the link to WorldAnvil.
    :param to_parse:
    :return:
    """
    output = f"Want to read more about the Dark Forest? Look here: {settings['links']['worldanvil']}"
    return output


def zephnos(to_parse=None):
    """
    Displays the recap video for the Zephnos arc.
    :param to_parse: None
    :return:
    """
    output = f"Curious about the Dark Forest? Watch the recap video for Zephnos' arc here: {settings['links']['zephnos_arc']}"
    return output


# ============================================== Account Linking =======================================================
def linkaccount(to_parse):
    account_id = to_parse.content.split()[1]
    alias_to_add = to_parse.author.name

    matches = re.match("[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}", account_id)

    if matches:
        hf.register_alias(alias_to_add, account_id)
        return "Successfully linked account!"
    else:
        return "Invalid account id. Please fix any typos and try again."


def accountid(to_parse):
    author = to_parse.author.name
    user_id = hf.get_user_id(author)

    if not user_id:
        hf.create_new_user(author, 0, 0)
        user_id = hf.get_user_id(author)

    return f"To link, go to the platform you want to link and type !linkaccount {user_id} to finish the linking process."


# ============================================= Campgrounds Functions ==================================================
def addlogs(to_parse):
    """
    Adds this number of logs to the fire
    :param to_parse: The string with the command output.
    :return:
    """
    output = ""

    if len(to_parse.content.lower().split()) > 1:
        user = to_parse.author.name
        add_value = int(to_parse.content.lower().split()[1])
        if hf.get_log_count(user) >= add_value > 0:
            campfire_count = hf.get_campfire_count() + add_value
            hf.set_campfire_count(campfire_count)
            hf.set_log_count(user, hf.get_log_count(user) - add_value)
            output = f"{to_parse.author.name} added {add_value} logs to the campfire. " \
                     f"There are now {campfire_count} logs in the fire."
        else:
            output = "You either don't have enough logs for that or the amount is invalid."

    return output


def campfire(to_parse=None):
    """
    Gets the campfire value
    :param to_parse: None
    :return: The campfire value as an integer
    """
    output = f"There are {hf.get_campfire_count()} logs in the central bonfire."

    return output


def givelogs(to_parse):
    """
    Gives logs from one player to another.
    :param to_parse:
    :return:
    """
    message = to_parse.content
    matches = re.match("!givelogs (\w*) (\d+)", message, flags=re.I)

    if matches:
        # target = message.split()[1]
        # amount = int(message.split()[2])
        target = matches.group(1)
        amount = int(matches.group(2))
        output = "Something went wrong"

        users = hf.get_user_list()
        author_name = to_parse.author.name

        # set the values
        if author_name.lower() in users:
            if hf.get_log_count(author_name) > amount:
                hf.set_log_count(target, hf.get_log_count(target) + amount)
                hf.set_log_count(to_parse.author.name,
                                               hf.get_log_count(to_parse.author.name.lower()) - amount)
                output = f"{to_parse.author.name} gave {amount} logs to {target.lower()}."
            else:
                output = f"{to_parse.author.name}, you don't have the logs to do that."
        else:
            output = f"{to_parse.author.name} doesn't yet have any logs. Stick around to earn more."

        return output
    else:
        return "Correct syntax is !givelogs <target> <amount>"


def addvoteoption(to_parse):
    """
    Adds a vote option to the currently active profile.
    :param to_parse: Contains the option to be added.
    :return:
    """
    message = to_parse.content
    matches = re.match('!addvoteoption "(.+)"\s?(\d+)?', message, flags=re.I)

    if matches:
        game_name = matches.group(1)
        starting_amount = 0
        if matches.group(2):
            starting_amount = int(matches.group(2))

        hf.add_vote_option(game_name, starting_amount, hf.get_active_profile())
        return f"Successfully added {game_name}"
    else:
        return "No valid options found. Please put quotes around your option."


def deletevoteoption(to_parse):
    """
    Deletes the targeted object, or returns an error if the vote doesn't exist.
    :param to_parse:
    :return:
    """
    message = to_parse.content
    matches = re.match('!deletevoteoption (.+)', message, flags=re.I)

    if matches:
        target = matches.group(1)

        if hf.vote_exists(target):
            if hf.delete_vote_option(target, hf.get_active_profile()):
                return f"Successfully deleted {target}!"
            else:
                return f"Something went wrong."
        else:
            return f"Salamandbot couldn't find {target} in the current vote profile."
    else:
        return f"I don't understand what you're saying. Correct syntax is !deletevoteoption <game name>"


def checkoptions(to_parse=None):
    """
    Displays all of the vote options, with how many logs each option has.
    :param to_parse: Expected none
    :return:
    """
    return_value = ''
    votes = hf.get_vote_data()
    active = hf.get_active_profile()
    options = {}

    # build a dictionary of values out of the options
    for option in votes["Profiles"][active]:
        options[option] = hf.get_vote_option_value(option)

    if not len(options.keys()):
        return "There's nothing in this profile. Add options with !addvoteoption."

    # sort by the keys https://stackoverflow.com/questions/613183/how-do-i-sort-a-dictionary-by-value
    sorted_files = sorted(options.items(), key=operator.itemgetter(1))

    # add all sorted values to retval and return.
    for x, y in reversed(sorted_files):
        return_value += str(x)

        # if the value is higher than 0, add the value
        if options[x] > 0:
            return_value += '('+str(y)+' logs)'

        return_value += ', '

    return_value = return_value[:-2]

    # sends the final message
    return return_value


def shields(to_parse=None):
    """
    Returns the current number of shields around the fire.
    :param to_parse:
    :return:
    """
    shield_count = hf.get_shield_count()
    output = f"There are {shield_count} shields around the fire. Keep them safe and they'll keep you safe."

    return output


def vote(to_parse, vote_manager: VoteManager):
    """
    Handles voting behavior for users.
    :param to_parse: Expected data to input into the Vote Manager
    :param vote_manager: The vote manager to add the vote to.
    :return:
    """

    def convert_seconds(amount):
        # time calculation
        seconds_to_completion = int(
            ((amount - float(max_vote_rate)) / float(max_vote_rate)) * cooldown_time)
        minutes_to_completion = 0
        hours_to_completion = 0
        if seconds_to_completion > 60:
            minutes_to_completion = seconds_to_completion / 60
            seconds_to_completion = seconds_to_completion % 60
        if minutes_to_completion > 60:
            hours_to_completion = minutes_to_completion / 60
            minutes_to_completion = minutes_to_completion % 60

        hours_to_completion = int(hours_to_completion)
        minutes_to_completion = int(minutes_to_completion)
        seconds_to_completion = int(seconds_to_completion)

        # send users a message to inform them how long logs will add for.
        if hours_to_completion != 0:
            return f"You have been added to the continuous add list. Logs will continue to add for " \
                   f"{hours_to_completion} hours and {minutes_to_completion} minutes and " \
                   f"{seconds_to_completion} seconds. Type \"!vote stop\" to stop voting on this choice. "
        elif minutes_to_completion != 0:
            return f"You have been added to the continuous add list. Logs will continue to add for " \
                   f"{minutes_to_completion} minutes and " \
                   f"{seconds_to_completion} seconds. Type \"!vote stop\" to stop voting on this choice. "
        else:
            return f"You have been added to the continuous add list. Logs will continue to add for " \
                   f"{seconds_to_completion} seconds. Type \"!vote stop\" to stop voting on this choice. "

    max_vote_rate = settings['settings']['max_vote_rate']
    cooldown_time = settings['settings']['cooldown_time']

    message = to_parse.content
    user = to_parse.author.name

    vote_data = hf.get_vote_data()

    matches = re.match('!vote (.+) (all)|!vote (.+) (\d+)|!vote stop', message, flags=re.I)

    output = ""

    if matches:
        if user in hf.get_users_on_cooldown() and matches.group(0).lower() != "!vote stop":
            cooldown_end = vote_data["Users On Cooldown"][user]["cooldown end"]
            return f"You won't be able to vote for another {int(cooldown_end - time.time())} seconds."

        vote_all = matches.group(2) != None
        amount = matches.group(4)
        target = matches.group(3) if not vote_all else matches.group(1)

        vote_options = vote_data["Profiles"][hf.get_active_profile()].keys()

        if matches.group(0).lower() == "!vote stop":
            if user in hf.get_users_on_cooldown():
                if hf.get_vote_data()["Users On Cooldown"][user]["amount"] != 0:
                    vote_manager.stop_voting(user)
                    return f"{user} has been removed from continuous voting. " \
                           f"You may now vote freely once the cooldown expires."
            else:
                return f"You are not currently voting on anything."

        if target not in vote_options:
            return "Salamandbot scratches in the dirt. Spelling? Capitalization? A missing number? " \
                   "It didn't know what that story was."

        if vote_all:
            hf.set_vote_option_value(target, hf.get_vote_option_value(target) + max_vote_rate)
            hf.set_log_count(user, hf.get_log_count(user) - max_vote_rate)
            hf.add_vote_contributor(target, user, "all")
            hf.set_last_vote_time(target, time.time())
            cooldown = hf.get_dynamic_cooldown_amount(max_vote_rate)
            hf.add_user_to_cooldown(user, time.time() + cooldown, target, "all")
            output += f"You've been added to continuous adding. You will add to {target} until you run out of logs. " \
                      f"Type \"!vote stop\" to stop adding at any time."
            return output
        else:
            try:
                amount = int(amount)
                user_logs = hf.get_log_count(user)
                if amount > user_logs:
                    return "You don't have enough logs for that."

                if amount > max_vote_rate:
                    hf.set_vote_option_value(target, hf.get_vote_option_value(target) + max_vote_rate)
                    hf.set_log_count(user, hf.get_log_count(user) - max_vote_rate)
                    hf.add_vote_contributor(target, user, amount)
                    continuous_cooldown = time.time() + hf.get_dynamic_cooldown_amount(max_vote_rate)
                    hf.add_user_to_cooldown(user, continuous_cooldown,
                                            target, amount - max_vote_rate)
                    hf.set_last_vote_time(target, time.time())
                    output += convert_seconds(amount + max_vote_rate)

                else:
                    hf.set_vote_option_value(target, hf.get_vote_option_value(target) + amount)
                    hf.set_log_count(user, hf.get_log_count(user) - amount)
                    hf.add_vote_contributor(target, user, amount)
                    cooldown = hf.get_dynamic_cooldown_amount(amount)
                    hf.add_user_to_cooldown(user, time.time() + cooldown, target, 0)
                    output += f"{user} added {amount} logs to {target}'s campfire. It now sits at " \
                              f"{hf.get_vote_option_value(target)}"
                return output
            except ValueError as e:
                return f"The value {amount} is not an integer. Please enter an integer."

    else:
        return "Salamandbot shakes its head. It scratches several words in the sand: !vote <name> <amount>."


# ======================================== Woodchips ===================================================================
def woodchips(to_parse=None):
    """
    Displays how many woodchips a user has.
    :param to_parse:
    :return:
    """
    output = f"{to_parse.author.name} has gathered {hf.get_woodchips(to_parse.author.name.lower())} woodchips."
    return output


def redeem(to_parse=None):
    """
    Redeems a specified redeemable.
    :param to_parse: The information on what to redeem
    :return:
    """
    message = to_parse.content
    message_args = message.split()
    arg_count = len(message_args)
    user = to_parse.author.name

    if arg_count == 1:
        return "Here are the redeemable options: recap, drink, pet, story, break, add, move, top."

    redeemables = {
        "recap": redeemable.Redeemable("recap", "Recap that story Newt!", -200, user),
        "drink": redeemable.Redeemable("drink", "Take a drink!", -500, user),
        "pet": redeemable.Redeemable("pet", "Pet that cat!", -600, user),
        "story": redeemable.Redeemable("story", "Story time!", -1000, user),
        "break": redeemable.Redeemable("break", "Time to hit the road.", -3000, user)
    }

    if arg_count >= 3:
        args = " ".join(message.split(" ")[2:])
        redeemables["add"] = redeemable.Redeemable("add", "Adding your game to the list!", -20000,
                                                   user, hf.add_to_votes, args)
        redeemables["move"] = redeemable.Redeemable("move", "Moving " + args + " to the top of the list!", -30000,
                                                    user, hf.move_option_to_top, args)
        redeemables["top"] = redeemable.Redeemable("top", "Adding and moving " + args + " to the top of the list!",
                                                   -45000,
                                                   user, hf.create_and_move, args)

    if message_args[1] in redeemables.keys():
        if arg_count == 2:
            if redeemables[message_args[1].lower()].redeem():
                return redeemables[message_args[1].lower()].description
            else:
                return "You don't have enough woodchips for that."
        if arg_count >= 3:
            if redeemables[message_args[1].lower()].redeem():
                return redeemables[message_args[1].lower()].description
            else:
                return "You don't have enough woodchips for that."


# ============================================ Story ===================================================================
def story(to_parse):

    output = ''

    message = to_parse.content
    message_args = message.split()
    arg_count = len(message_args)
    user = to_parse.author.name

    # parse the input to something usable by the script
    data_input = message.split()[2:]
    title = ' '.join(data_input)

    # two word commands
    if arg_count == 2:
        if message_args[1].lower() == "display":
            return hf.display_story_list()
        if message_args[1].lower() == "selected":
            story_list = hf.load_story_list()
            output = ""
            for story in hf.get_selected_stories_list():
                output += f"{story_list[story]['name']},"
            return output[:-1]
        if message_args[1].lower() == "roll":
            if hf.get_selected_stories_list():
                output = hf.roll_story()[1]
                return output
            else:
                output = hf.roll_unselected_story()[1]
                return output
        if message_args[1].lower() == "pending":
            return hf.display_pending_list()
        if message_args[1].lower() == "links":
            return hf.display_pending_links()

    # single word commands
    if arg_count == 1:
        return hf.display_story_list()

    # variable length commands
    if arg_count > 1:
        if message_args[1].lower() == "info":
            return f"Info for {title}: {hf.story_info(data_input)}"
        if message_args[1].lower() == "select":
            story_added = hf.select_story(title, user)
            if story_added:
                return f"Added {title} to the next story spin."
            else:
                return "That story is already in the next story spin."
        if message_args[1].lower() == "add":
            title = ' '.join(data_input[:-1])
            # get the final value and save is as the link
            info = message_args[arg_count - 1].lower()

            if data_input:
                return hf.add_story(title, info, user)
        if message_args[1].lower() == ("remove" or "subtract"):
            return hf.remove_story(title)
        if message_args[1].lower() == "restore":
            return hf.re_add(title)
        if message_args[1].lower() == "approve":
            return hf.approve_story(title)
        if message_args[1].lower() == "reject":
            return hf.reject_story(title)


def stories(to_parse):
    return story(to_parse)