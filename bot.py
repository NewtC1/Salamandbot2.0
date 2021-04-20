import argparse
import logging
import os
import utils.commands as command_list
import utils.helper_functions as helper_functions

from utils.clock import Clock
from input_parser import InputParser as Input
from pathlib import Path
from twitch_bot import TwitchBot

settings = helper_functions.load_settings()

def parse_args():
    """
    Parses launcher arguments
    :return:
    """
    argument_parser = argparse.ArgumentParser(description='Process some integers.')
    argument_parser.add_argument('-l', '--logfile', type=Path, default=Path('Salamandbot2.log'),
                                 help="Path, with filename, to write the log to")

    return argument_parser.parse_args()


def generate_missing_values():
    """
    Scans for the value files and generates anything that's currently missing.
    :return:
    """

    campfire_dir = os.path.join(os.path.dirname(__file__), settings['directories']['campfire'])
    shield_dir = os.path.join(os.path.dirname(__file__), settings['directories']['shields_file'])
    points_dir = os.path.join(os.path.dirname(__file__), settings['directories']['points_file'])
    votes_dir = os.path.join(os.path.dirname(__file__), settings['directories']['votes_file'])
    logs_dir = os.path.join(os.path.dirname(__file__), settings['directories']['logs_file'])

    def generate_value(file_dir, default_value=""):
        """
        Generates files with the specified default values.
        :param file_dir: The directory to generate.
        :param default_value: The value of an empty file.
        :return:
        """
        if not os.path.exists(file_dir):
            with open(file_dir, encoding="utf-8-sig",mode="w+") as file:
                file.write(default_value)
            logging.info(f"[Bot] Generating missing values file for {file_dir}")

    generate_value(campfire_dir, "0")
    generate_value(shield_dir, "0")
    generate_value(points_dir, "{}")
    generate_value(votes_dir, "{}")
    generate_value(logs_dir, "{}")


def tick():
    """
    This is the function handed to the global clock.
    :return:
    """
    return


args = parse_args()

file_log = logging.FileHandler(args.logfile, encoding='utf-8')
logging.basicConfig(handlers=[file_log], level=logging.INFO,
                    format="{asctime}:{levelname}:{name}:{message}", style="{")

if __name__ == "__main__":

    # parses inputs
    logging.info("[Bot] Creating input parser")
    parser = Input(logger=logging.getLogger())

    # ticks on a seperate thread and handles functions as they are resolved.
    logging.info("[Bot] Creating clock")
    clock_thread = Clock(logger=logging.getLogger(), function_dict={tick: ""}, tick_frequency=60)
    clock_thread.start()

    # create any files that are missing
    generate_missing_values()

    # add commands
    # TODO: Automate this later so we don't have to add these one by one
    logging.info("[Bot] Adding commands")
    parser.add_command("!commands", command_list.commands)
    parser.add_command("!addlogs", command_list.addlogs)
    parser.add_command("!zephnos", command_list.zephnos)
    parser.add_command("!campfire", command_list.campfire)

    bots = [TwitchBot(parser)]

    logging.info("[Bot] Starting bots...")
    for bot in bots:
        bot.run()
