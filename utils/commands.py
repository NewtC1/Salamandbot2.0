import os
import toml
from utils import helper_functions

settings = toml.load(os.path.join(os.path.dirname(__file__), "settings.toml"))

def commands(to_parse):
    """

    :param content: None expected
    :return:
    """
    output = f"Commands can be found here: {settings['links']['commands']}"
    return output


def zephnos(to_parse):
    """
    Displays the recap video for the Zephnos arc.
    :param content: None
    :return:
    """
    output = f"Curious about the Dark Forest? Watch the recap video for Zephnos' arc here: {settings['links']['zephnos_arc']}"
    return output


# ============================================= Campgrounds Functions ==================================================
def addlogs(to_parse):
    """
    Adds this number of logs to the fire
    :param content: The string with the command output.
    :return:
    """
    output = ""

    if len(to_parse.content.lower().split()) > 1:
        add_value = int(to_parse.content.lower().split()[1])
        campfire_count = helper_functions.get_campfire_count() + add_value
        helper_functions.set_campfire_count(campfire_count)
        output = f"{to_parse.author.name} added {add_value} logs to the campfire. There are now {campfire_count} logs in the fire."

    return output


def campfire(to_parse):
    """
    Gets the campfire value
    :param to_parse: None
    :return: The campfire value as an integer
    """
    output = f"There are {helper_functions.get_campfire_count()} logs in the central bonfire."

    return output

