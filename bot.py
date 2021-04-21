import argparse
import asyncio
import logging
import os
import utils.commands as command_list
import utils.helper_functions as helper_functions

from inspect import getmembers, isfunction
from utils.clock import Clock
from input_parser import InputParser as Input
from pathlib import Path
from twitch_bot import TwitchBot
from twitchAPI.twitch import Twitch

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
    print("Tick!")
    return


async def start_loop():
    # parses inputs
    logging.info("[Bot] Creating input parser")
    parser = Input(logger=logging.getLogger())

    # ticks on a seperate thread and handles functions as they are resolved.
    logging.info("[Bot] Creating clock")
    clock = Clock(logger=logging.getLogger(), function_dict={tick: ""}, tick_frequency=3)

    # create any files that are missing
    generate_missing_values()

    # add commands
    logging.info("[Bot] Adding commands")
    commands = getmembers(command_list, isfunction)
    for command in commands:
        parser.add_command(f"!{command[0]}", command[1])

    logging.info("[Bot] Starting bots...")
    await asyncio.gather(clock.run(), TwitchBot(parser).start())


args = parse_args()

file_log = logging.FileHandler(args.logfile, encoding='utf-8')
logging.basicConfig(handlers=[file_log], level=logging.INFO,
                    format="{asctime}:{levelname}:{name}:{message}", style="{")

if __name__ == "__main__":
    asyncio.run(start_loop())
