import json
import os
import toml
import time
import requests
import uuid

settings_file = os.path.join(os.path.dirname(__file__), "settings.toml")

client_id = os.environ['CLIENT_ID']
client_secret = os.environ["CLIENTSECRET"]
target_channel = os.environ["CHANNEL"]

oauth_request = requests.post(
    f"https://id.twitch.tv/oauth2/token?client_id={client_id}&client_secret={client_secret}&grant_type=client_credentials")
irc_token = oauth_request.json()['access_token']


def load_settings(file=settings_file):
    return toml.load(file)


settings = load_settings()
campfire_file = os.path.join(os.path.dirname(__file__), '..', settings['directories']['campfire'])
logs_file = os.path.join(os.path.dirname(__file__), '..', settings['directories']['logs_file'])
shields_file = os.path.join(os.path.dirname(__file__), '..', settings['directories']['shields_file'])
woodchips_file = os.path.join(os.path.dirname(__file__), '..', settings['directories']['woodchips_file'])
votes_file = os.path.join(os.path.dirname(__file__), '..', settings['directories']['votes_file'])
accounts_file = os.path.join(os.path.dirname(__file__), '..', settings['directories']['accounts_file'])
base_cooldown = settings['settings']['cooldown_time']
max_vote_rate = settings['settings']['max_vote_rate']


def get_vote_option_value(option):
    option_value = 0
    data = get_vote_data()
    active = data["Active Profile"]
    if option in data["Profiles"][active].keys():
        option_value = data["Profiles"][active][option]["vote value"]

    return option_value


def change_woodchips(user, amount):
    accounts = load_accounts()
    user_id = get_user_id(user)

    if user_id:
        if (accounts[user_id]["woodchips"] + amount) < 0:
            return False

        accounts[user_id]["woodchips"] += amount
        update_accounts(accounts)
    else:
        create_new_user(user, woodchips=amount)

    return True


def load_challenges():
    """Loads the points json."""

    with open(woodchips_file, "r", encoding="utf-8-sig") as json_file:
        woodchips = json.load(json_file)

    return woodchips


def update_challenges(points_data):
    """Saves the data."""
    with open(woodchips_file, "w+", encoding="utf-8-sig") as json_file:
        points = json.dumps(points_data, indent=4)
        json_file.write(points)

    return points


def get_woodchips(user):
    accounts = load_accounts()
    user_id = get_user_id(user)

    if user_id:
        return accounts[user_id]["woodchips"]
    else:
        return 0


def set_woodchip_count(user, amount):
    accounts = load_accounts()
    user_id = get_user_id(user)

    if user_id:
        accounts[user_id]["woodchips"] = amount
        update_accounts(accounts)
    else:
        create_new_user(user, amount)


def get_vote_data():
    with open(votes_file, encoding='utf-8-sig', mode='r') as f:
        vote_data = json.load(f)

    return vote_data


def update_vote_data(data):
    with open(votes_file, encoding='utf-8-sig', mode='w+') as file:
        json.dump(data, file, indent='\t')


def vote_exists(target):
    data = get_vote_data()
    if target in data["Profiles"][get_active_profile()].keys():
        return True
    else:
        return False


def set_vote_option_value(target, new_value):
    data = get_vote_data()
    if vote_exists(target):
        data["Profiles"][get_active_profile()][target]['vote value'] = new_value
    update_vote_data(data)


def get_active_profile():
    data = get_vote_data()
    return_value = data["Active Profile"]
    return return_value


def add_vote_option(target, value, profile):
    data = get_vote_data()
    data['Profiles'][profile][target] = {
        "vote value": value,
        "length of game": 0,
        "votes list": {
        },
        "last added": time.time(),
        "contributor": ""
    }
    update_vote_data(data)


def delete_vote_option(target, profile):
    data = get_vote_data()
    if data['Profiles'][profile].pop(target, None):
        update_vote_data(data)
        return True
    else:
        return False


def set_last_vote_time(target, new_value):
    data = get_vote_data()
    if vote_exists(target):
        data["Profiles"][get_active_profile()][target]['last added'] = new_value
    update_vote_data(data)


def add_vote_contributor(target, user, amount):
    data = get_vote_data()
    amount_to_add = amount if not type(amount) == str else max_vote_rate
    if user in data['Profiles'][get_active_profile()][target]['votes list'].keys():
        data['Profiles'][get_active_profile()][target]['votes list'][user] += amount_to_add
    else:
        data['Profiles'][get_active_profile()][target]['votes list'][user] = amount_to_add
    update_vote_data(data)


def get_campfire_count():
    with open(campfire_file, encoding='utf-8-sig', mode='r') as file:
        campfire_count = int(file.read())

    return campfire_count


def set_campfire_count(new_count: int):
    with open(campfire_file, encoding='utf-8-sig', mode='w') as file:
        file.write(str(new_count))


def get_log_count(user):
    data = load_accounts()

    user_id = get_user_id(user)

    if user_id:
        return data[user_id]["logs"]
    else:
        return 0


def set_log_count(user, value):
    data = load_accounts()
    user_id = get_user_id(user)
    if user_id:
        data[user_id]["logs"] = value
        update_accounts(data)
    else:
        create_new_user(user, 0, value)


def get_shield_count():
    with open(shields_file, "r", encoding="utf-8-sig") as file:
        shields = int(file.read())

    return shields


def set_shield_count(value):
    with open(shields_file, "w+", encoding="utf-8-sig") as file:
        file.write(str(value))


def get_users_on_cooldown() -> list:
    return list(get_vote_data()["Users On Cooldown"].keys())


def add_user_to_cooldown(user, cooldown_end, target, amount):
    data = get_vote_data()
    data["Users On Cooldown"][user] = {
                                       "cooldown end": cooldown_end,
                                       "target": target,
                                       "amount": amount
                                       }
    update_vote_data(data)


def remove_user_from_cooldown(user) -> bool:
    data = get_vote_data()

    if user in data["Users On Cooldown"].keys():
        del data["Users On Cooldown"][user]
        update_vote_data(data)
        return True
    else:
        return False


def get_dynamic_cooldown_amount(amount) -> int:
    dynamic_cooldown_amount = int((amount/max_vote_rate)*base_cooldown)
    return dynamic_cooldown_amount


def load_accounts() -> dict:
    with open(accounts_file, "r", encoding="utf-8-sig") as file_stream:
        data = json.load(file_stream)

    return data


def update_accounts(data: dict):
    with open(accounts_file, "w+", encoding="utf-8-sig") as file_stream:
        json.dump(data, file_stream, indent="\t")


def get_user_id(username) -> str:
    accounts = load_accounts()
    matching_account = ""
    for account in accounts.keys():
        if username in accounts[account]['aliases']:
            matching_account = account

    return matching_account


def register_alias(alias, user_id):
    accounts = load_accounts()
    accounts[user_id]["aliases"].append(alias)

    old_user_id = get_user_id(alias)
    if old_user_id:
        accounts[user_id]["logs"] += accounts[old_user_id]["logs"]
        accounts[user_id]["woodchips"] += accounts[old_user_id]["woodchips"]
        del accounts[old_user_id]

    update_accounts(accounts)


def create_new_user(alias, woodchips=0, logs=0):
    accounts = load_accounts()
    accounts[str(uuid.uuid1())] = {"aliases": [alias], "woodchips": woodchips, "logs": logs, "active_name": alias}
    update_accounts(accounts)


def get_user_list() -> list:
    accounts = load_accounts()
    usernames = []

    for account in accounts:
        usernames.extend(accounts[account]["aliases"])

    return usernames
