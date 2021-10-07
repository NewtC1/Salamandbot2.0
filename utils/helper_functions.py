import json
import os
import toml
import time
from playsound import playsound
import requests
import uuid
import random
import events.MoonriseArtifacts.Artifact as Artifact

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
sfx_file = os.path.join(os.path.dirname(__file__), '..', settings['directories']['sfx_file'])
accounts_file = os.path.join(os.path.dirname(__file__), '..', settings['directories']['accounts_file'])
story_file = os.path.join(os.path.dirname(__file__), '..', settings['directories']['story_file'])
base_cooldown = settings['settings']['cooldown_time']
max_vote_rate = settings['settings']['max_vote_rate']
loyalty_blacklist = settings["loyalty_points"]["loyalty_blacklist"]


def get_vote_option_value(option, profile_override=None):
    active_profile = get_active_profile()
    if profile_override:
        active_profile = profile_override
    option_value = 0
    data = get_vote_data()
    if option in data["Profiles"][active_profile].keys():
        option_value = data["Profiles"][active_profile][option]["vote value"]

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


def get_woodchip_count(user):
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


def vote_exists(target, profile_override=None):
    active_profile = get_active_profile()

    if profile_override:
        active_profile = profile_override

    data = get_vote_data()
    if target in data["Profiles"][active_profile].keys():
        return True
    else:
        return False


def set_vote_option_value(target, new_value, profile_override=None):
    active_profile = get_active_profile()

    if profile_override:
        active_profile = profile_override

    data = get_vote_data()
    if vote_exists(target, active_profile):
        data["Profiles"][active_profile][target]['vote value'] = new_value
    update_vote_data(data)


def get_active_profile():
    data = get_vote_data()
    return_value = data["Active Profile"]
    return return_value


def set_active_profile(target):
    data = get_vote_data()
    data["Users On Cooldown"] = {}
    profiles = data["Profiles"].keys()
    if target in profiles:
        data["Active Profile"] = target
        update_vote_data(data)
        return True
    else:
        return False


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


def set_last_vote_time(target, new_value, profile_override=None):
    data = get_vote_data()
    if vote_exists(target):
        data["Profiles"][get_active_profile()][target]['last added'] = new_value
    update_vote_data(data)


def add_vote_contributor(target, user, amount, profile_override=None):
    active_profile = get_active_profile()

    if profile_override:
        active_profile = profile_override

    data = get_vote_data()
    amount_to_add = amount if not type(amount) == str else max_vote_rate
    if user in data['Profiles'][active_profile][target]['votes list'].keys():
        data['Profiles'][active_profile][target]['votes list'][user] += amount_to_add
    else:
        data['Profiles'][active_profile][target]['votes list'][user] = amount_to_add
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


def load_shields():
    with open(shields_file, "r", encoding="utf-8-sig") as file:
        shields = json.load(file)

    return shields


def update_shields(shield_dict):
    with open(shields_file, "w+", encoding="utf-8-sig") as file:
        json.dump(shield_dict, file)


def get_shield_count():
    shields = load_shields()

    return shields["shield_count"]


def set_shield_count(value):
    shields = load_shields()
    shields["shield_count"] = int(value)
    update_shields(shields)


def get_shield_damage():
    shields = load_shields()
    return shields["shield_damage"]


def set_shield_damage(value):
    shields = load_shields()
    shields["shield_damage"] = value
    update_shields(shields)


def get_users_on_cooldown() -> list:
    return list(get_vote_data()["Users On Cooldown"].keys())


def add_user_to_cooldown(user, cooldown_end, target, amount):
    data = get_vote_data()
    data["Users On Cooldown"][user] = {
                                       "cooldown end": cooldown_end,
                                       "target": target,
                                       "amount": amount,
                                       "profile": get_preferred_profile(user)
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


def play_audio(target: str):
    if not os.path.exists(target):
        return False

    playsound(target)
    return True


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

    if alias not in accounts[user_id]["aliases"]:
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


def get_preferred_profile(username) -> str:
    accounts = load_accounts()
    user_id = get_user_id(username)
    return_value = ''

    # preferred_profile is guaranteed to be correct if it exists, so no new testing needed here.
    if "preferred_profile" in accounts[user_id].keys():
        return_value = accounts[user_id]['preferred_profile']

    return return_value


# =============================================== Artifact Storage =====================================================
# This is very experimental
def get_user_artifact(username: str) -> Artifact.Artifact or None:
    """
    Returns an artifact constructed from the information stored in a user's account, or none if the user doesn't have
    one.
    :param username:
    :return:
    """

    user_id = get_user_id(username)
    data = load_accounts()
    # lists all subclasses names
    artifact_subclass_names = [cls.__name__ for cls in Artifact.Artifact.__subclasses__()]
    artifact_subclasses = [Artifact.Artifact.__subclasses__()]

    subclass_dict = {}
    for i in range(len(artifact_subclass_names)):
        subclass_dict[artifact_subclass_names[i]] = artifact_subclasses[0][i]

    # subclass_dict = {artifact_subclass_names[i]: artifact_subclasses[i] for i in range(len(artifact_subclass_names)-1)}
    return_value = None
    if user_id:
        if "artifact_type" in data[user_id].keys():
            return_object = subclass_dict[data[user_id]["artifact_type"]](uses=data[user_id]["artifact_uses"])
            return_value = return_object

    return return_value


def set_user_artifact(username, artifact: Artifact.Artifact):
    user_id = get_user_id(username)
    data = load_accounts()
    data[user_id]["artifact_type"] = artifact.__class__.__name__
    data[user_id]["artifact_uses"] = artifact.get_uses()

    update_accounts(data)


def get_user_artifact_uses(username: str):
    user_id = get_user_id(username)
    accounts = load_accounts()
    if "artifact_type" in accounts[user_id].keys():
        return accounts[user_id]["artifact_uses"]
    else:
        pass
        # raise NoUserArtifactError("", "No user artifact has been defined.")


def set_user_artifact_uses(username: str, value: int):
    user_id = get_user_id(username)
    accounts = load_accounts()
    if "artifact_type" in accounts[user_id].keys():
        accounts[user_id]["artifact_uses"] = value
        update_accounts(accounts)
    else:
        pass
        # raise NoUserArtifactError("", "No user artifact has been defined.")


# ============================================= Story Interaction ======================================================
def load_story_list():
    """Returns a the list of counters as a settings object"""
    with open(story_file, encoding='utf-8-sig', mode='r') as f:
        data = json.load(f)["approved"]

    return data


def update_story_list(story_list):
    data = load_story_file()

    data["approved"] = story_list

    with open(story_file, encoding='utf-8-sig', mode='w') as filestream:
        json.dump(data, filestream, indent="\t")


def load_pending_list():
    """Returns a the list of counters as a settings object"""
    with open(story_file, encoding='utf-8-sig', mode='r') as f:
        data = json.load(f)["pending"]

    return data


def update_pending_list(story_list):
    data = load_story_file()

    data["pending"] = story_list

    with open(story_file, encoding='utf-8-sig', mode='w') as filestream:
        json.dump(data, filestream, indent="\t")


def load_story_file():
    with open(story_file, encoding='utf-8-sig', mode='r') as f:
        data = json.load(f)

    return data


def update_story_file(data: dict):
    with open(story_file, encoding='utf-8-sig', mode='w') as f:
        json.dump(data, f, indent="\t")


# display all available stories
def display_story_list():
    data = load_story_list()
    retval = ''
    for key in data.keys():
        # get rid of the last space
        retval += data[key]['name'] + ', '

    return retval[:-2]


# display all available stories
def display_pending_list():
    data = load_story_file()
    retval = ''
    for key in data["pending"].keys():
        retval += f"{data['pending'][key]['name']}, "

    retval = retval[:-2]

    return retval


def display_pending_links():
    data = load_story_file()
    retval = ''
    for key in data["pending"].keys():
        output = key + ": " + data["pending"][key]["info"]

        # get rid of the last space
        retval += output + ' , '

    return retval[:-2]


def get_selected_stories_list():
    data = load_story_file()

    return data["selected"]


# returns the story info
def story_info(story):
    data = load_story_list()
    if story.lower() in data.keys():
        return data[story.lower()]["info"]
    else:
        return "The story " + story + " is not in the story selection yet. Send me a link and I can add it."


# select a story
def select_story(story: str, user):

    data = load_story_file()
    selected_stories = get_selected_stories_list()
    if story.lower() in data["approved"].keys():
        if story.lower() not in selected_stories:
            data["selected"].append(story.lower())
            if data["approved"][story.lower()]["contributor"] != user.lower():
                # add more points each time anyone other than the user selects it
                data["approved"][story.lower()]["value"] += 50
            update_story_file(data)
            return True
        else:
            return False
    else:
        return False


# select a story from chosen stories
def roll_story():
    choice = random.choice(get_selected_stories_list())
    selection_name = story_name(choice)
    retval = f"The story that was selected was: {selection_name}. You can follow along at {story_info(choice)}."

    if story_author(choice):
        retval = f"The story that was selected was: {selection_name} written by {story_author(choice)}." \
                 f" You can follow along at {story_info(choice)}."

    # reset selected stories
    data = load_story_file()
    data["selected"] = []
    if data["approved"][choice]["value"] > 0:
        user = data["approved"][choice.lower()]["contributor"]
        value = data["approved"][choice.lower()]["value"]
        set_log_count(user, get_log_count(user) + value)

    update_story_file(data)

    # remove the story we rolled from the list
    remove_story(choice.lower())

    return retval, retval


def roll_unselected_story():
    data = load_story_list()
    stories = data.keys()
    choice = random.choice(list(stories))
    selection_name = story_name(choice)
    retval = "Rolling from the main story list. The story that was selected was: " + story_name(
        choice) + ". You can follow along at " + story_info(
        choice)

    if story_author(choice):
        retval = f"The story that was selected was: {selection_name} written by {story_author(choice)}." \
                 f" You can follow along at {story_info(choice)}."

    user = data[choice.lower()]["contributor"]
    value = data[choice.lower()]["value"]
    set_log_count(user.lower(), get_log_count(user.lower()) + value)

    remove_story(choice.lower())

    return retval, retval


# add a story
def add_story(story, info, contributor, author=""):
    output = ""
    if story.lower() in (load_pending_list() or load_story_list()):
        return "That story already exists."
    # else if the counter does not exist
    else:
        # add the counter to the counters.json
        pending_list = load_pending_list()
        storyname = story.lower()
        pending_list[storyname] = {}
        pending_list[storyname]["info"] = info
        pending_list[storyname]["contributor"] = contributor
        pending_list[storyname]["value"] = 0
        pending_list[storyname]["name"] = story
        pending_list[storyname]["author"] = author

        # give logs to the user who added
        set_log_count(contributor, get_log_count(contributor) + settings["events"]["submission_reward"])

        # save the story
        update_pending_list(pending_list)
        output = f'Story "{story}" successfully created. It has been stored in pending.'

    return output


def approve_story(story: str):
    """
    Moves a story from the pending file to the story file.
    :param story: The story to approve.
    :return:
    """

    pending_data = load_pending_list()
    story_to_approve = pending_data[story.lower()]
    del pending_data[story.lower()]
    update_pending_list(pending_data)

    story_data = load_story_list()
    story_data[story.lower()] = story_to_approve
    update_story_list(story_data)

    return f'Story "{story_name(story)}" has been approved.'


def reject_story(story: str):
    """
    Removes a story from the approval list.
    :param story: The story to reject.
    :return:
    """

    pending_data = load_pending_list()

    if story.lower() in pending_data.keys():
        del pending_data[story.lower()]
        update_pending_list(pending_data)
        return f"Removed story {story} from pending."
    else:
        return f"Could not remove {story} from the pending stories."


# remove a story from the list
def remove_story(story):
    data = load_story_file()
    remove_name = story_name(story)
    # save the story for restoration if we need to
    data["removed"][story.lower()] = data["approved"][story.lower()]
    del data["approved"][story.lower()]
    # update the story file with the removed story
    with open(story_file, encoding='utf-8-sig', mode='w+') as f:
        json.dump(data, f, indent="\t")

    if story.lower() not in data["approved"].keys():
        return f"Successfully removed {remove_name} from the approved options."
    else:
        return f"Something went wrong."


def re_add(story):
    data = load_story_file()
    story_lower = story.lower()

    if story_lower in data["removed"].keys():
        data["approved"][story_lower] = data["removed"][story_lower]
        del data["removed"][story_lower]
        update_story_file(data)

        return f'Story "{story_name(story_lower)}" successfully restored.'
    return  f'Story "{story}" could not be restored.'


def story_name(story):
    data = load_story_list()
    return data[story.lower()]["name"]


def story_contributor(story):
    data = load_story_list()
    return data[story.lower()]["contributor"]


def story_author(story):
    data = load_story_list()
    if data[story]["author"]:
        return data[story.lower()]["author"]

    return ""

# ========================================= Redeemable Support Functions ===============================================
def add_to_votes(option):
    add_vote_option(option, 0, get_active_profile())
    return


def move_option_to_top(option):
    data = get_vote_data()

    values = list(data["Profiles"][get_active_profile()][vote]["vote value"] for vote in data["Profiles"][get_active_profile()].keys())
    top_value = max(values)

    data["Profiles"][get_active_profile()][option]["vote value"] = top_value
    update_vote_data(data)


def create_and_move(option):
    add_to_votes(option)
    move_option_to_top(option)