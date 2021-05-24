import argparse
import asyncio
import json
import logging
import os
import utils.commands as command_list
import utils.helper_functions as helper_functions

from inspect import getmembers, isfunction
from utils.clock import Clock
from input_parser import InputParser as Input
from pathlib import Path
from twitch_bot import TwitchBot

settings = helper_functions.load_settings()
bots = {}
is_active = False

TWITCH_CHANNEL = os.environ['CHANNEL']
BOT_TICK_RATE = 600
WOODCHIP_PAYOUT_RATE = 32

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
    points_dir = os.path.join(os.path.dirname(__file__), settings['directories']['woodchips_file'])
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
    points_template = json.dumps({
        "Challenges": {

        },
        "Users": {

        }
    })
    generate_value(points_dir, points_template)
    generate_value(votes_dir, "{}")
    default_log_value = {}
    generate_value(logs_dir, json.dumps(default_log_value))


async def payout_logs(users=None):
    shields = helper_functions.get_shield_count()
    data = helper_functions.load_logs()

    users_in_chat = users
    if not users:
        users_in_chat = await bots["twitch"].get_chatters(TWITCH_CHANNEL)
    for user in users_in_chat[8]:
        helper_functions.set_log_count(user, helper_functions.get_log_count(user) + shields)
        logging.info(f"[Logs] {user} gained {shields} logs.")


async def payout_woodchips(users=None):
    data = helper_functions.load_points()
    users_in_chat = users
    if not users:
        users_in_chat = await bots["twitch"].get_chatters(TWITCH_CHANNEL)
    for user in users_in_chat[8]:
        helper_functions.set_points(user, helper_functions.get_log_count(user) + WOODCHIP_PAYOUT_RATE)
        logging.info(f"[Woodchips] {user} gained {WOODCHIP_PAYOUT_RATE} woodchips.")


async def user_is_in_chat(user):
    global bots
    retval = False
    for bot in bots.keys():
        users_in_chat = await bots[bot].get_chatters(TWITCH_CHANNEL)
        print(f"Users in chat: {users_in_chat[8]}")
        if user in users_in_chat[8]:
            print(f"{user} is in chat!")
            retval = True
            break

    return retval


async def tick():
    """
    This is the function handed to the global clock.
    :return:
    """
    global bots
    global is_active
    global is_live

    # check for the bot going live.
    # await update_active_status()
    await update_live_status()
    if is_live:
        users_in_chat = await bots["twitch"].get_chatters(TWITCH_CHANNEL)
        await payout_logs(users_in_chat)
        await payout_woodchips(users_in_chat)

    return


async def update_active_status():
    """
    Updates active status when called.
    :return:
    """
    global is_active

    if not is_active:
        for key in bots.keys():
            is_active = await bots[key].chat_is_active()
    else:
        no_live_stream = True
        for key in bots.keys():
            if await bots[key].chat_is_active():
                no_live_stream = False
        is_active = not no_live_stream


async def update_live_status():
    """
    Updates live status when called.
    :return:
    """
    global is_live
    channel_status = []

    for key in bots.keys():
        channel_status.append(await bots[key].is_live())

    if any(channel_status):
        is_live = True
    else:
        is_live = False


async def start_loop():
    # parses inputs
    logging.info("[Bot] Creating input parser...")
    parser = Input(logger=logging.getLogger())

    # ticks on a seperate thread and handles functions as they are resolved.
    logging.info("[Bot] Creating clocks...")
    clock = Clock(logger=logging.getLogger(), function_dict={tick: ""}, tick_frequency=BOT_TICK_RATE)

    # create any files that are missing
    generate_missing_values()

    # add commands
    logging.info("[Bot] Adding commands...")
    commands = getmembers(command_list, isfunction)
    for command in commands:
        parser.add_command(f"!{command[0]}", command[1])

    logging.info("[Bot] Starting bots...")
    bots["twitch"] = TwitchBot(parser)

    await asyncio.gather(clock.run(), bots["twitch"].start())


args = parse_args()

file_log = logging.FileHandler(args.logfile, encoding='utf-8')
logging.basicConfig(handlers=[file_log], level=logging.INFO,
                    format="{asctime}:{levelname}:{name}:{message}", style="{")

if __name__ == "__main__":
    asyncio.run(start_loop())
