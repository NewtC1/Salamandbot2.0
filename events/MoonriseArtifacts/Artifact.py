import re
import logging


class Artifact:
    """
    Artifacts class for use with Cicero's ability.
    """

    def __init__(self, name, description, uses, cost: str = "0l", function=None):
        """
        Artifacts have many different features, most of which are set by subclasses. Functions refer to what the
        artifact does and is a function object.
        :param name: Name of the artifact.
        :param description: Description of the artifact.
        :param uses: Number of uses remaining.
        :param cost: Cost in logs or woodchips. This is a string. 45l for logs or 23w for woodchips.
        :param function: The ability associated with the artifact.
        :param function_params: Parameters needed for the artifact.
        """
        self.name = name
        self.description = description
        self.uses = uses

        match = re.match("(\d+)(l|w)", cost)
        if match:
            self.cost = {"type": match.group(2), "value": int(match.group(1))}
        else:
            logging.info(f"[Artifact] Failed to find a valid cost for artifact {self.name}, defaulting to 0l")
            self.cost = {"type": "l", "value": 0}

        self.function = function

    def use(self, *args):
        """
        Users the associated function, if applicable. Reduces the number of users by 1.
        :return:
        """

        if self.function:
            return self.function(*args)
        else:
            return "The object appears to be useless. Or maybe you're not using it correctly?"

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_description(self):
        return self.description

    def set_description(self, new_descrip):
        self.description = new_descrip

    def get_uses(self):
        return self.uses

    def set_uses(self, value):
        self.uses = value

    def set_function(self, function):
        self.function = function

    def get_cost_type(self):
        return self.cost["type"]

    def get_cost_value(self):
        return self.cost["value"]