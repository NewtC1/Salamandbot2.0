import logging
import os

import utils.helper_functions as hf
import asyncio


class InputParser:

    input_queue = []
    commands = {}

    def __init__(self, logger=None, active_clock=None, vote_manager=None, moonrise_manager=None,
                 rimeheart_manager = None):
        """
        Listens for results fired from input sources
        """
        self.logger = logger
        self.clock = active_clock
        self.vote_manager = vote_manager
        self.moonrise_manager = moonrise_manager
        self.rimeheart_manager = rimeheart_manager
        self.bots = []

    def parse_input(self, source, to_parse=None):
        """
        Parses input from the source.
        :param source:
        :param to_parse:
        :return:
        """
        content = ""
        output_prefix = ""

        # Get the message content based on which
        if source == "twitch":
            content = to_parse.content.lower()
            output_prefix = "/me "
        elif source == "discord":
            content = to_parse.content.lower()
        elif source == "youtube":
            content = to_parse.content.lower()

        if content:
            first_word = content.split()[0]  # Gets the first word of the input to determine the command it should run
        else:
            return ""

        output = ""
        if first_word == "!vote" or first_word == '!prefer': # requires special command lines due to needing access to the vote manager
            output = f"{output_prefix}{self.commands[first_word](to_parse, vote_manager=self.vote_manager)}"
        elif first_word == "!imp" or first_word == "!soil" or first_word == "!bjorn" or first_word == "!cicero": # requires special command lines due to needing access to the moonrise manager
            output = f"{output_prefix}{self.commands[first_word](to_parse, moonrise_manager=self.moonrise_manager)}"
        elif first_word == "!raffle" or first_word == "!rafflechoice":
            output = f"{output_prefix}{self.commands[first_word](to_parse, rimeheart_manager=self.rimeheart_manager)}"
        elif first_word in self.commands.keys():
            output = f"{output_prefix}{self.commands[first_word](to_parse)}"
        else:
            # send the message to all other bots if it's not a command
            display_name = hf.get_user_active_name(to_parse.author.name)
            names_to_ignore = [os.environ["YOUTUBE_BOT_CHANNEL_ID"], os.environ["BOT_NICK"]]
            if display_name not in names_to_ignore:
                output = f"[{display_name}] {to_parse.content}"
                for bot in self.bots:
                    loop = asyncio.get_running_loop()
                    coroutine = bot.send_message(output)
                    loop.create_task(coroutine)

            return ""

        return output

    def add_command(self, command_name, command_func):
        """
        Adds a command to the command list.
        :param command_name: The name of the command being added.
        :param command_func: The function associated with the command.
        :return: True if the command was successfully added, false if it already exists
        """

        if command_name not in self.commands.keys():
            self.commands[command_name] = command_func
            return True
        else:
            logging.info(f"[Input Parser]{command_name} is already a command in this current parser.")
            return False

    def save_commands(self):
        pass

    def add_bot(self, bot):
        self.bots.append(bot)
