import os
import toml
import time
import re
import operator
import requests
import data_classes.redeemable as redeemable
import utils.sfx as sfx_module
import utils.obfuscate_module
from inspect import getmembers, isfunction
from utils import helper_functions as hf
from time import time
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


def kingmaker(to_parse=None):
    """
    Outputs a link to the recap episodes.
    :param to_parse:
    :return:
    """
    return "The story so far: https://www.youtube.com/playlist?list=PLSQSsMCgp5bCn9dGMsCvSYRazL-VHW_j7"


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
    output = f"Rules for moonrise can be found here: {settings['links']['moonrise']}"
    return output


def obfuscate(to_parse):
    """
    Obfuscates the phrase the user inputs.
    :param to_parse:
    :return:
    """
    message = to_parse.content
    phrase = " ".join(message.split()[1:])

    return utils.obfuscate_module.obfuscate(phrase)


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


def sfx(to_parse=None):
    sfx_commands = getmembers(sfx_module, isfunction)

    output = ""
    for command in sfx_commands:
        output += f"!{command[0]}, "

    output = output[:-2]

    return output


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


def prefer(to_parse, vote_manager):
    """
    Command for users to change account preferences
    :param to_parse:
    :return:
    """
    message = to_parse.content
    author = to_parse.author.name
    account_id = hf.get_user_id(author)
    message_args = message.split()
    accounts = hf.load_accounts()
    vote_data = hf.get_vote_data()
    return_value = f''

    if len(message_args) == 1:
        return f'The following subcommands exist: profile'

    if len(message_args) == 2:
        if message_args[1] == "profile":
            if "preferred_profile" in accounts[account_id].keys():
                return_value += f"Here is your current preferred profile: {hf.get_preferred_profile(author)} "

            return_value += f'Here is a list of all current vote profiles: '
            for profile in vote_data["Profiles"].keys():
                return_value += profile + ', '
            return return_value
    if len(message_args) > 2:
        if message_args[1] == "profile":
            target_profile = " ".join(message_args[2:])
            if target_profile == "clear" and "preferred_profile" in accounts[account_id].keys():
                del accounts[account_id]['preferred_profile']
                hf.update_accounts(accounts)
                return "Preferences for profiles have been cleared."
            if target_profile in vote_data["Profiles"].keys():
                if author not in hf.get_users_on_cooldown():
                    accounts[account_id]["preferred_profile"] = target_profile
                    hf.update_accounts(accounts)
                    return "Successfully set a default vote profile."
                else:
                    return "Please wait until your vote cooldown finishes before changing profiles."
            else:
                return 'That profile does not exist.'


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

            # rimeheart log expenditure tracking.
            if settings["events"]["rimeheart_active"]:
                hf.add_logs_spent(user, add_value)
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
    matches = re.match('!addvoteoption "(.+)"\s?(\d+)?\s?(\w+)?', message, flags=re.I)

    if matches:
        game_name = matches.group(1)
        starting_amount = 0
        target_profile = hf.get_active_profile()
        if matches.group(2):
            starting_amount = int(matches.group(2))
        if matches.group(3):
            target_profile = matches.group(3)

        output = f"Successfully added game {game_name}."
        add_output = hf.add_vote_option(game_name, starting_amount, target_profile)
        return output + add_output
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


def selectnextgame(to_parse) -> str:
    """
    Selects the next game on the active list.
    :param to_parse:
    :return:
    """

    hf.get_active_profile()
    return " "


def checkoptions(to_parse=None):
    """
    Displays all of the vote options, with how many logs each option has.
    :param to_parse: Expected none
    :return:
    """
    author = to_parse.author.name
    votes = hf.get_vote_data()
    active = hf.get_active_profile(author)
    options = {}

    return_value = f'Profile: {active}. '

    # build a dictionary of values out of the options
    for option in votes["Profiles"][active]:
        options[option] = hf.get_vote_option_value(option, author)

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

    max_vote_rate = settings['settings']['max_vote_rate']
    cooldown_time = settings['settings']['cooldown_time']

    message = to_parse.content
    user = to_parse.author.name
    active_profile = hf.get_active_profile(user)

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

    vote_data = hf.get_vote_data()

    matches = re.match('!vote (.+) (all)|!vote (.+) (\d+)|!vote stop', message, flags=re.I)

    output = ""

    if matches:
        if user in hf.get_users_on_cooldown() and matches.group(0).lower() != "!vote stop":
            cooldown_end = vote_data["Users On Cooldown"][user]["cooldown end"]
            return f"You won't be able to vote for another {int(cooldown_end - time())} seconds."

        vote_all = matches.group(2) != None
        amount = matches.group(4)
        target = matches.group(3) if not vote_all else matches.group(1)

        vote_options = list(vote_data["Profiles"][active_profile].keys())
        # used for case matching
        vote_options_lower = [option.lower() for option in vote_options]

        if matches.group(0).lower() == "!vote stop":
            if user in hf.get_users_on_cooldown():
                if hf.get_vote_data()["Users On Cooldown"][user]["amount"] != 0:
                    vote_manager.stop_voting(user)
                    return f"{user} has been removed from continuous voting. " \
                           f"You may now vote freely once the cooldown expires."
            else:
                return f"You are not currently voting on anything."

        if target.lower() not in vote_options_lower:
            return "Salamandbot scratches in the dirt. Spelling? Capitalization? A missing number? " \
                   "It didn't know what that story was."
        else:
            target = vote_options[vote_options_lower.index(target.lower())]

        vote_multiplier = vote_manager.calculate_multiplier(target)

        if vote_all:
            hf.set_vote_option_value(target, hf.get_vote_option_value(target) + int(vote_multiplier*max_vote_rate))
            hf.set_log_count(user, hf.get_log_count(user) - max_vote_rate)
            hf.add_vote_contributor(target, user, "all")
            hf.set_last_vote_time(target, time(), user)
            cooldown = hf.get_dynamic_cooldown_amount(max_vote_rate)
            hf.add_user_to_cooldown(user, time() + cooldown, target, "all")
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
                    hf.set_vote_option_value(target, hf.get_vote_option_value(target, user) + int(vote_multiplier*max_vote_rate), user)
                    hf.set_log_count(user, hf.get_log_count(user) - max_vote_rate)
                    hf.add_vote_contributor(target, user, max_vote_rate)
                    continuous_cooldown = time() + hf.get_dynamic_cooldown_amount(max_vote_rate)
                    hf.add_user_to_cooldown(user, continuous_cooldown,
                                            target, amount - max_vote_rate)
                    hf.set_last_vote_time(target, time(), user)
                    output += convert_seconds(amount + max_vote_rate)

                else:
                    hf.set_log_count(user, hf.get_log_count(user) - amount)
                    hf.set_vote_option_value(target, hf.get_vote_option_value(target, user) + int(vote_multiplier*amount),
                                             user)
                    hf.add_vote_contributor(target, user, amount)
                    hf.set_last_vote_time(target, time(), user)
                    cooldown = hf.get_dynamic_cooldown_amount(amount)
                    hf.add_user_to_cooldown(user, time() + cooldown, target, 0)
                    output += f"{user} added {int(amount*vote_multiplier)} logs to {target}'s campfire. It now sits at " \
                              f"{hf.get_vote_option_value(target, user)}"
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
    output = f"{to_parse.author.name} has gathered {hf.get_woodchip_count(to_parse.author.name)} woodchips."
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
        return "Here are the redeemable options: recap: 200, quiz: 300, drink: 500, pet: 600, break: 3000, " \
               "add: 20000, move: 30000, top: 45000."

    redeemables = {
        "recap": redeemable.Redeemable("recap", "Recap that story Newt!", -200, user),
        "drink": redeemable.Redeemable("drink", "Take a drink!", -500, user),
        "pet": redeemable.Redeemable("pet", "Pet that cat!", -600, user),
        "break": redeemable.Redeemable("break", "Time to hit the road.", -3000, user),
        "quiz": redeemable.Redeemable("quiz", "Quiz me!", -300, user)
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
            return f"Info for {title}: {hf.story_info(title)}"
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

# ==================================================== Moonrise ========================================================


def bjorn(to_parse, moonrise_manager):
    return_value = ""
    message = to_parse.content
    # splinter command
    if message.split()[1].lower() == "splinter":
        return moonrise_manager.bjorn_splinter()

    # delay command
    elif message.split()[1].lower() == "delay":
        return moonrise_manager.bjorn_delay()

    else:
        return 'Bjorn looks up at you in confusion, but doesn\'t speak. He clearly didn\'t understand you.'


def soil(to_parse, moonrise_manager):
    message = to_parse.content
    if len(message.split()) < 2:
        return "\"Sup?\""

    if message.split()[1] == "kill":
        return moonrise_manager.soil_kill()

    # restore command. resets the shield's damage value.
    elif message.split()[1] == "restore":
        return moonrise_manager.soil_restore()
    else:
        return '"You wanna try saying that again? I don\'t know what moonspeak that was, but it wasn\'t something ' \
               'I\'m fluent in."'


def cicero(to_parse, moonrise_manager):
    message = to_parse.content

    if len(message.split()) < 2:
        return "Cicero looks up expectantly, his wide eyes locked on you. \"A sale?\""

    if message.split()[1] == "buy":
        return moonrise_manager.cicero_buy(to_parse.author.name)
    elif message.split()[1] == "check":
        return moonrise_manager.cicero_check(to_parse.author.name)
    elif message.split()[1] == "use":
        return moonrise_manager.cicero_use(to_parse.author.name)
    elif message.split()[1] == "sale":
        return moonrise_manager.cicero_sale()
    else:
        return 'Cicero holds out an inch-long talon to stop you. "I do not know what language you speak. ' \
               'Please, try once more."'


def imp(to_parse, moonrise_manager):
    return_value = ""
    message = to_parse.content
    if len(message.split()) > 1:
        answer = " ".join(message.split(" ")[1:])
        result = moonrise_manager.current_attacker.check_answer(answer)
        moonrise_manager.pending_imp_results.append(result)
        # get rid of the imp after they try and answer the question
        delay = moonrise_manager.kill_attacker()
        return f"The imp disappears with a rude noise and a cackle. The last thing you hear is \"{result}.\""
    else:
        return moonrise_manager.current_attacker.riddle


# ===================================================== Rimeheart ======================================================
def raffle(to_parse, rimeheart_manager):
    return_value = ""
    message = to_parse.content
    author = to_parse.author.name

    if len(message.split()) > 1:
        try:
            amount = int(message.split()[1])
            return_value = rimeheart_manager.buy_multiple_raffles(author, amount)
        except ValueError:
            return "That's not a valid value. Please give uncle Cicero a correct number."
    else:
        return_value = rimeheart_manager.buy_raffle(author)

    return return_value


def rafflechoice(to_parse, rimeheart_manager):
    return_value = f"The current raffle option is {rimeheart_manager.current_game}."
    return return_value


def topspenders(to_parse):
    accounts = hf.load_accounts()
    spenders = {}
    for account in accounts:
        if "logs_spent" in accounts[account].keys():
            spenders[accounts[account]["active_name"]] = accounts[account]["logs_spent"]

    sorted_spenders = {k: v for k,v in sorted(spenders.items(), key=lambda item: item[1], reverse=True)}

    output = ""
    count = 1
    for spender in sorted_spenders.keys():
        output += f"{count}: {spender}({sorted_spenders[spender]} logs), "
        count += 1

    output = output[:-2]

    return output
