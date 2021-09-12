import argparse
import asyncio
import json
import logging
import os

from inspect import getmembers, isfunction
from utils.clock import Clock
from input_parser import InputParser as Input
from pathlib import Path
from bots.twitch_bot import TwitchBot
from bots.discord_bot import DiscordBot
import utils.commands as command_list
import utils.helper_functions as helper_functions
from voting.vote_manager import VoteManager
import events.overheat as overheat
import events.stories as stories

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

    campfire_dir = helper_functions.campfire_file
    shield_dir = helper_functions.shields_file
    woodchips_dir = helper_functions.woodchips_file
    votes_dir = helper_functions.votes_file
    logs_dir = helper_functions.logs_file
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
    accounts_template = {}
    generate_value(accounts_dir, json.dumps(accounts_template))
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


async def payout_logs(users=None):
    shields = helper_functions.get_shield_count()
    log_gain_multiplier = settings["settings"]["log_gain_multiplier"]

    users_in_chat = users
    logging.info(f"[Logs] Users in chat: {users_in_chat}")
    if not users:
        users_in_chat = await bots["twitch"].get_chatters(TWITCH_CHANNEL)
    for user in users_in_chat[1]:
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
    for user in users_in_chat[1]:
        if user not in helper_functions.loyalty_blacklist:
            helper_functions.set_woodchip_count(user, helper_functions.get_log_count(user) + WOODCHIP_PAYOUT_RATE)
            # logging.info(f"[Woodchips] {user} gained {WOODCHIP_PAYOUT_RATE} woodchips.")


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
        await payout_logs(users_in_chat)
        await payout_woodchips(users_in_chat)
        helper_functions.set_campfire_count(helper_functions.get_campfire_count() - 20)

    return


async def overheat_tick():
    global is_live

    if is_live:
        overheat_output = overheat.overheat()
        if overheat_output:
            for bot in bots.keys():
                await bots[bot].send_message(overheat_output)


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
    # manages votes as users input them
    logging.info("[Bot] Creating vote manager...")
    vote_manager = VoteManager(logger=logging.getLogger())

    story_manager = stories.StoryManager()

    # ticks on a seperate thread and handles functions as they are resolved.
    logging.info("[Bot] Creating clocks...")
    clock = Clock(logger=logging.getLogger(), function_dict={tick: "",
                                                             story_manager.tick: ""}, tick_frequency=BOT_TICK_RATE)
    vote_clock = Clock(logger=logging.getLogger(),
                       function_dict={vote_manager.tick_vote: "",
                                      vote_manager.remove_users_from_cooldown: "",
                                      vote_manager.decay: "",
                                      overheat_tick: ""
                                      },
                       tick_frequency=1)

    # parses inputs
    logging.info("[Bot] Creating input parser...")
    parser = Input(logger=logging.getLogger(), vote_manager=vote_manager)

    # create any files that are missing
    generate_missing_values()

    # add commands
    logging.info("[Bot] Adding commands...")
    commands = getmembers(command_list, isfunction)
    for command in commands:
        parser.add_command(f"!{command[0]}", command[1])

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

    print(f"Commands: {parser.commands}")

    # starting bots
    logging.info("[Bot] Starting bots...")
    bots["twitch"] = TwitchBot(parser)
    discord = DiscordBot(parser)
    vote_manager.bots = [bots["twitch"]]

    await asyncio.gather(clock.run(), bots["twitch"].start(), discord.start(os.environ["DISCORD_TOKEN"]), vote_clock.run())


args = parse_args()

file_log = logging.FileHandler(args.logfile, encoding='utf-8')
logging.basicConfig(handlers=[file_log], level=logging.INFO,
                    format="{asctime}:{levelname}:{name}:{message}", style="{")

if __name__ == "__main__":
    try:
        asyncio.run(start_loop())
    finally:
        pass
