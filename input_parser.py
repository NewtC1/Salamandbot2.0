import logging

class InputParser:

    input_queue = []
    commands = {}

    def __init__(self, logger=None, active_clock=None, vote_manager=None):
        """
        Listens for results fired from input sources
        :param input_sources: The bots that are sending events to the input parser
        """
        self.logger = logger
        self.clock = active_clock
        self.vote_manager = vote_manager

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
            pass

        if content:
            first_word = content.split()[0]  # Gets the first word of the input to determine the command it should run
        else:
            return ""

        output = ""
        if first_word == "!vote": # requires special command lines due to needing access to the vote manager
            output = f"{output_prefix}{self.commands[first_word](to_parse, vote_manager=self.vote_manager)}"
        elif first_word in self.commands.keys():
            output = f"{output_prefix}{self.commands[first_word](to_parse)}"

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