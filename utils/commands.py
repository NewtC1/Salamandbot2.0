import os
import toml
import re
from utils import helper_functions

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
    output = f"{to_parse.author.name} has gathered {helper_functions.get_log_count(to_parse.author.name.lower())} logs."
    return output


def lurk(to_parse=None):
    """
    Display a lurk message. Also gives the user a single log if they don't already have one.
    :param to_parse:
    :return:
    """
    output = f"{to_parse.author.name} pulls up a log and sits down to enjoy the stories."

    log_data = helper_functions.load_logs()

    users = log_data.keys()
    author_name = to_parse.author.name

    if author_name in users:
        if helper_functions.get_log_count(author_name) == 0:
            helper_functions.set_log_count(author_name.lower(), 1)
    else:
        helper_functions.set_log_count(author_name.lower(), 1)

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
    Displays the overheat text.
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


# ============================================= Campgrounds Functions ==================================================
def addlogs(to_parse):
    """
    Adds this number of logs to the fire
    :param to_parse: The string with the command output.
    :return:
    TODO: Remove logs from the user's log count
    """
    output = ""

    if len(to_parse.content.lower().split()) > 1:
        add_value = int(to_parse.content.lower().split()[1])
        campfire_count = helper_functions.get_campfire_count() + add_value
        helper_functions.set_campfire_count(campfire_count)
        output = f"{to_parse.author.name} added {add_value} logs to the campfire. " \
                 f"There are now {campfire_count} logs in the fire."

    return output


def campfire(to_parse=None):
    """
    Gets the campfire value
    :param to_parse: None
    :return: The campfire value as an integer
    """
    output = f"There are {helper_functions.get_campfire_count()} logs in the central bonfire."

    return output


def givelogs(to_parse):
    """
    Gives logs from one player to another.
    :param to_parse:
    :return:
    """
    message = to_parse.content
    matches = re.match("!givelogs (\w*) (\d+)", message)

    if matches:
        # target = message.split()[1]
        # amount = int(message.split()[2])
        target = matches.group(1)
        amount = int(matches.group(2))
        output = "Something went wrong"

        log_data = helper_functions.load_logs()

        users = log_data.keys()
        author_name = to_parse.author.name

        # set the values
        if author_name.lower() in users:
            if log_data[to_parse.author.name.lower()] > amount:
                helper_functions.set_log_count(target, helper_functions.get_log_count(target) + amount)
                helper_functions.set_log_count(to_parse.author.name,
                                               helper_functions.get_log_count(to_parse.author.name.lower()) - amount)
                output = f"{to_parse.author.name} gave {amount} logs to {target.lower()}."
            else:
                output = f"{to_parse.author.name}, you don't have the logs to do that."
        else:
            output = f"{to_parse.author.name} doesn't yet have any logs. Stick around to earn more."

        return output
    else:
        return "Correct syntax is !givelogs <target> <amount>"


def vote(to_parse=None):
    """
    Handles voting behavior for users.
    :param to_parse:
    :return:
    """
    pass


def shields(to_parse=None):
    """
    Returns the current number of shields around the fire.
    :param to_parse:
    :return:
    """
    shield_count = helper_functions.get_shield_count()
    output = f"There are {shield_count} shields around the fire. Keep them safe and they'll keep you safe."

    return output
