import argparse
import asyncio
import json
import logging
import os
import sys

from inspect import getmembers, isfunction
from utils.clock import Clock
from input_parser import InputParser as Input
from pathlib import Path

from bots.twitch_bot import TwitchBot
from bots.discord_bot import DiscordBot
from bots.youtube_bot import YouTubeBot

import utils.commands as command_list
import utils.helper_functions as helper_functions

from voting.vote_manager import VoteManager

import events.overheat as overheat
import events.stories as stories
import events.moonrise as moonrise
import events.rimeheart as rimeheart

settings = helper_functions.load_settings()
bots = {}

TWITCH_CHANNEL = os.environ['CHANNEL']
BOT_TICK_RATE = 600
WOODCHIP_PAYOUT_RATE = 32
is_live = False
reminders_position = 0


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

    campfire_dir = helper_functions.campfire_file
    shield_dir = helper_functions.shields_file
    woodchips_dir = helper_functions.woodchips_file
    votes_dir = helper_functions.votes_file
    accounts_dir = helper_functions.accounts_file

    def generate_value(file_dir, default_value=""):
        """
        Generates files with the specified default values.
        :param file_dir: The directory to generate.
        :param default_value: The value of an empty file.
        :return:
        """
        if not os.path.exists(file_dir):
            with open(file_dir, encoding="utf-8-sig", mode="w+") as file:
                file.write(default_value)
            logging.info(f"[Bot] Generating missing values file for {file_dir}")

    generate_value(campfire_dir, "0")

    shield_template = json.dumps({
        "shield_count": 0,
        "shield_damage": 0
    })
    generate_value(shield_dir, shield_template)

    woodchips_template = json.dumps({
        "Challenges": {}
    })
    generate_value(woodchips_dir, woodchips_template)

    votes_template = json.dumps({
        "Last Decay": 0,
        "Users On Cooldown": {},
        "Active Profile": "Default",
        "Active Profile Schedule": {},
        "Profiles": {
            "Default": {}
        }
    })
    generate_value(votes_dir, votes_template)

    accounts_template = {
        }
    generate_value(accounts_dir, json.dumps(accounts_template))

    stories_template = json.dumps({
        "removed": {},
        "selected": [],
        "approved": {},
        "pending": {}
    })
    generate_value(helper_functions.story_file, stories_template)

    moonrise_status_template = json.dumps({
        "soil_ready": True,
        "bjorn_ready": True,
        "bjorn_delay": True,
        "soil_kill": True,
        "bjorn_splinter": True,
        "artifact_effects": []
    })
    generate_value(helper_functions.moonrise_status_file, moonrise_status_template)

    rimeheart_giveaway_template = json.dumps({
        "valid_codes": {},
        "invalid_codes": {},
        "skipped_codes": {}
    })
    generate_value(rimeheart.rimeheart_dir, rimeheart_giveaway_template)


async def update_user_roles(users=None):
    users_in_chat = users
    if not users:
        users_in_chat = await bots["twitch"].get_chatters(TWITCH_CHANNEL)
    roles = {"broadcaster": users_in_chat.broadcaster,
             "vip": users_in_chat.vips,
             "moderator": users_in_chat.moderators,
             "viewer": users_in_chat.viewers}

    for role in roles.keys():
        for user in roles[role]:
            user_id = helper_functions.get_user_id(user)
            result = helper_functions.add_user_role(user_id, role)
            if result:
                logging.info(f"[Bot] {result}")


async def payout_logs(users=None):
    shields = helper_functions.get_shield_count()
    log_gain_multiplier = settings["settings"]["log_gain_multiplier"]

    users_in_chat = users
    logging.info(f"[Logs] Users in chat: {users_in_chat}")
    if not users:
        users_in_chat = await bots["twitch"].get_chatters(TWITCH_CHANNEL)
    for user in users_in_chat:
        if user not in helper_functions.loyalty_blacklist:
            logs_gained = int(shields*log_gain_multiplier)
            helper_functions.set_log_count(user, helper_functions.get_log_count(user) + logs_gained)
            # logging.info(f"[Logs] {user} gained {logs_gained} logs.")


async def payout_woodchips(users=None):
    data = helper_functions.load_accounts()
    users_in_chat = users
    logging.info(f"[Woodchips] Users in chat: {users_in_chat}")
    if not users:
        users_in_chat = await bots["twitch"].get_chatters(TWITCH_CHANNEL)
    for user in users_in_chat:
        if user not in helper_functions.loyalty_blacklist:
            helper_functions.set_woodchip_count(user, helper_functions.get_woodchip_count(user) + WOODCHIP_PAYOUT_RATE)
            # logging.info(f"[Woodchips] {user} gained {WOODCHIP_PAYOUT_RATE} woodchips.")


async def user_is_in_chat(user):
    global bots
    retval = False
    for bot in bots.keys():
        users_in_chat = await bots[bot].get_chatters(TWITCH_CHANNEL)
        print(f"Users in chat: {users_in_chat}")
        if user in users_in_chat:
            print(f"{user} is in chat!")
            retval = True
            break

    return retval


# Tick functions
async def tick():
    """
    This is the function handed to the global clock.
    :return:
    """
    global bots
    global is_live

    # check for the bot going live.
    # await update_active_status()
    await update_live_status()
    if is_live:
        # TODO: Make this channel type agnostic.
        users_in_chat = await bots["twitch"].get_chatters(TWITCH_CHANNEL)

        # await payout_logs(users_in_chat)
        # await payout_woodchips(users_in_chat)
        # await update_user_roles(users_in_chat)
        # helper_functions.set_campfire_count(helper_functions.get_campfire_count() - 20)

    return


async def reminders(reminders: list = helper_functions.settings["strings"]["reminders"]):
    """ These are reminders the bot regularly throws up while live."""
    global is_live
    global reminders_position
    if is_live:
        if len(reminders) < 1:
            return

        output = reminders[reminders_position]
        reminders_position += 1
        if reminders_position >= len(reminders):
            reminders_position = 0

        for bot in bots:
            if bot != "!discord":
                await bots[bot].send_message(output)


async def overheat_tick(manager: overheat.OverheatManager):
    global is_live
    if is_live and settings["events"]["overheat_active"]:
        overheat_output = manager.tick()
        if overheat_output:
            for bot in bots.keys():
                await bots[bot].send_message(overheat_output)


async def moonrise_tick(manager: moonrise.MoonriseManager):
    global is_live
    if is_live and settings["events"]["moonrise_active"]:
        moonrise_output = manager.tick()
        if moonrise_output:
            for bot in bots.keys():
                await bots[bot].send_message(moonrise_output)


async def rimeheart_tick(manager: rimeheart.RimeheartManager):
    global is_live
    if is_live and settings["events"]["rimeheart_active"]:
        rimeheart_output = manager.tick()
        if rimeheart_output:
            for bot in bots.keys():
                await bots[bot].send_message(rimeheart_output)


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
        if not is_live:
            logging.info("[Bot] Live status changed to True.")
        is_live = True
    else:
        if is_live:
            logging.info("[Bot] Live status changed to False.")
        is_live = False


async def start_loop(end_loop=None):
    # create any files that are missing
    logging.info("[Bot] Generating any missing values...")
    generate_missing_values()

    # manages votes as users input them
    logging.info("[Bot] Creating vote manager...")
    vote_manager = VoteManager(logger=logging.getLogger())

    logging.info("[Bot] Creating Story manager...")
    story_manager = stories.StoryManager()
    moonrise_manager = moonrise.MoonriseManager(logger=logging.getLogger())
    rimeheart_manager = rimeheart.RimeheartManager()
    overheat_manager = overheat.OverheatManager()

    # ticks on a seperate thread and handles functions as they are resolved.
    logging.info("[Bot] Creating clocks...")
    clock = Clock(logger=logging.getLogger(), function_dict={story_manager.tick: ""}, tick_frequency=BOT_TICK_RATE)
    vote_clock = Clock(function_dict={vote_manager.tick_vote: "",
                                      vote_manager.remove_users_from_cooldown: "",
                                      vote_manager.decay: "",
                                      },
                       tick_frequency=1)
    moonrise_clock = Clock(function_dict={moonrise_tick: moonrise_manager}, tick_frequency=5)
    rimeheart_clock = Clock(function_dict={rimeheart_tick: rimeheart_manager}, tick_frequency=10)
    overheat_clock = Clock(function_dict={overheat_tick: overheat_manager}, tick_frequency=600)
    reminder_clock = Clock(function_dict={reminders: ""}, tick_frequency=1800)

    # parses inputs
    logging.info("[Bot] Creating input parser...")
    parser = Input(vote_manager=vote_manager, moonrise_manager=moonrise_manager,
                   rimeheart_manager=rimeheart_manager)

    # add sfx commands
    logging.info("[Bot] Adding sfx commands...")
    sfx_files = os.listdir(helper_functions.sfx_file)
    for sfx in sfx_files:
        # create the function with the same name as the sfx file
        sfx_file_path = os.path.join(helper_functions.sfx_file, sfx)

        if not os.path.exists(os.path.join(os.getcwd(), "utils/sfx.py")):
            with open("utils/sfx.py", "w+", encoding="utf-8-sig") as filestream:
                template = "import utils.helper_functions as helper_functions"
                filestream.write(template)

        with open("utils/sfx.py", "r", encoding="utf-8-sig") as filestream:
            data = filestream.read()

        sfx_name = sfx.split('.')[0]
        function = f"\ndef {sfx_name}(to_parse=None): " \
                   f"\n\thelper_functions.playsound(r\"{sfx_file_path}\") " \
                   f"\n\treturn \"Playing {sfx_name}.\""

        if function not in data:
            data += function

        with open("utils/sfx.py", "w", encoding="utf-8-sig") as filestream:
            filestream.write(data)

    import utils.sfx as sfx
    # add the function to the parser
    sfx_commands = getmembers(sfx, isfunction)
    for command in sfx_commands:
        parser.add_command(f"!{command[0]}", command[1])

    # add commands
    logging.info("[Bot] Adding commands...")
    commands = getmembers(command_list, isfunction)
    for command in commands:
        parser.add_command(f"!{command[0]}", command[1])

    print(f"Commands: {parser.commands}")

    # starting bots
    logging.info("[Bot] Starting bots...")
    bots["twitch"] = TwitchBot(parser)
    bots["youtube"] = YouTubeBot(parser)
    discord = DiscordBot(parser)
    vote_manager.bots = [bots["twitch"]]
    vote_manager.discord_bot = discord

    await asyncio.gather(clock.run(), bots["twitch"].start(), bots["youtube"].start(),
                         discord.start(os.environ["DISCORD_TOKEN"]),
                         vote_clock.run(), moonrise_clock.run(), rimeheart_clock.run(), reminder_clock.run(),
                         overheat_clock.run())

    if end_loop:
        loop = asyncio.get_running_loop()
        loop.stop()
        loop.close()


args = parse_args()

# file_log = logging.FileHandler(args.logfile, encoding='utf-8')
logging.basicConfig(filename=args.logfile, filemode="w", level=logging.INFO,
                    format="{asctime}:{levelname}:{name}:{message}", style="{")

if __name__ == "__main__":
    try:
        asyncio.run(start_loop())
    finally:
        os.execv(sys.argv[0], sys.argv)
