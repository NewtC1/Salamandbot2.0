import json
import os
import codecs
import toml

settings_file = os.path.join(os.path.dirname(__file__), "settings.toml")


def load_settings(file=settings_file):
    return toml.load(file)


settings = load_settings()
campfire_file = os.path.join(os.path.dirname(__file__), '..' ,settings['directories']['campfire'])

def get_vote_option_value(option):
    global vote_location
    option_value = 0
    data = get_vote_data()
    active = data["Active Profile"]
    if option in data["Profiles"][active].keys():
        option_value = data["Profiles"][active][option]["vote value"]

    return option_value


def change_points(user, amount):
    points = load_points()

    if user in points["Users"].keys():
        if (points["Users"][user] + amount) < 0:
            return False

    if user in points["Users"].keys():
        points["Users"][user] += amount
    else:
        points["Users"][user] = amount

    update_points(points)

    return True


def load_points():
    """Loads the points json."""

    with open(points_json, "r") as json_file:
        points = json.load(json_file, encoding="utf-8-sig")

    return points


def update_points(points_data):
    """Saves the data."""
    with open(points_json, "w+") as json_file:
        points = json.dumps(points_data, encoding="utf-8-sig", indent=4)
        json_file.write(points)

    return points


def get_points(user):
    points = load_points()

    if user in points["Users"].keys():
        return points["Users"][user]
    else:
        return 0


def get_stream_is_live():
    global stream_is_live

    return stream_is_live


def get_vote_data():
    with codecs.open(os.path.join(vote_location, "vote.json"), encoding='utf-8-sig', mode='r') as f:
        vote_data = json.load(f, encoding='utf-8-sig')

    return vote_data


def vote_exists(target):
    data = get_vote_data()
    if target in data["Profiles"][get_active_profile()].keys():
        return True
    else:
        return False


def get_active_profile():
    global vote_location
    data = get_vote_data()
    return data["Active Profile"]


def get_campfire_count():
    with open(campfire_file, encoding='utf-8-sig', mode='r') as file:
        campfire_count = int(file.read())

    return campfire_count


def set_campfire_count(new_count: int):
    with open(campfire_file, encoding='utf-8-sig', mode='w') as file:
        file.write(str(new_count))