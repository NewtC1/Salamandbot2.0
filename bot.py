import argparse
import logging

from input_parser import InputParser as Input
from pathlib import Path
from twitch_bot import TwitchBot



def parse_args():
    argument_parser = argparse.ArgumentParser(description='Process some integers.')
    argument_parser.add_argument('-l', '--logfile', type=Path, default=Path('Salamandbot2.log'),
                        help="Path, with filename, to write the log to")

    return argument_parser.parse_args()


args = parse_args()

file_log = logging.FileHandler(args.logfile, encoding='utf-8')
logging.basicConfig(handlers=[file_log], level=logging.INFO,
                    format="{asctime}:{levelname}:{name}:{message}", style="{")


def commands(content):
    command_link = "https://docs.google.com/document/d/1TLSf6pbiqqNrKha85TxqoJWIluovDWGaLId8_jTB4to/edit?usp=sharing"
    print(f"Commands can be found here: {command_link}")

if __name__ == "__main__":
    parser = Input(logger=logging.getLogger())
    parser.add_command("!commands", commands)

    bots = [TwitchBot(parser)]

    logging.info("")
    for bot in bots:
        bot.run()