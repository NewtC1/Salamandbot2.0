import argparse
import json
import logging
import os
import utils.commands as command_list
import utils.helper_functions as helper_functions

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

args = parse_args()

file_log = logging.FileHandler(args.logfile, encoding='utf-8')
logging.basicConfig(handlers=[file_log], level=logging.INFO,
                    format="{asctime}:{levelname}:{name}:{message}", style="{")

if __name__ == "__main__":
    parser = Input(logger=logging.getLogger())
    generate_missing_values()
    parser.add_command("!commands", command_list.commands)
    parser.add_command("!addlogs", command_list.addlogs)
    parser.add_command("!zephnos", command_list.zephnos)
    parser.add_command("!campfire", command_list.campfire)

    bots = [TwitchBot(parser)]

    logging.info("")
    for bot in bots:
        bot.run()