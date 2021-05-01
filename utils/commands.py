import os
import toml
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
        output = f"{to_parse.author.name} added {add_value} logs to the campfire. There are now {campfire_count} logs in the fire."

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
    target = message.split()[1]
    amount = int(message.split()[2])
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
