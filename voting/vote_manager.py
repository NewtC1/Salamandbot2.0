import os
import toml
import logging
import time
from utils import helper_functions as hf

settings = toml.load(os.path.join(os.path.dirname(__file__), "..\\utils\\settings.toml"))
base_cooldown = settings['settings']['cooldown_time']

# decay settings
decay_days = settings['settings']['decay_days']
decay_amount = settings['settings']['decay_amount']
max_vote_rate = settings['settings']['max_vote_rate']


class OutOfLogsException(Exception):
    pass


class VoteManager:

    def __init__(self, logger, votes=None, bots=None):
        self.vote_list = {}
        if votes:
            self.vote_list = votes
        self.logger = logger
        self.bots = bots

    async def apply_vote(self, target, voter, amount, profile):
        amount_to_increase = max_vote_rate

        if amount != "all":
            amount_to_increase = max_vote_rate if amount > max_vote_rate else amount
            new_amount = amount - amount_to_increase
            hf.add_user_to_cooldown(voter, time.time() + base_cooldown, target, new_amount)
        else:
            hf.add_user_to_cooldown(voter, time.time() + hf.get_dynamic_cooldown_amount(amount_to_increase), target,
                                    amount)

        if hf.get_log_count(voter) < amount_to_increase:
            raise OutOfLogsException

        hf.set_vote_option_value(target, hf.get_vote_option_value(target, profile) + amount_to_increase, profile)
        hf.add_vote_contributor(target, voter, amount_to_increase, profile)
        hf.set_log_count(voter, hf.get_log_count(voter) - amount_to_increase)

        hf.set_last_vote_time(target, time.time())

        return amount - amount_to_increase if amount != "all" else "all"

    async def tick_vote(self):

        def get_pending_profile_change():
            """
            Gets the next event that should occur given the current time.
            :return: The time of the next event, or None if there is no pending event.
            """

            # get the list of scheduled events
            schedule = hf.get_vote_data()["Active Profile Schedule"]

            if schedule:
                schedule_times = []
                now = time.localtime()
                for item_time in schedule.keys():
                    new_time = time.strptime(f"{now.tm_year} {now.tm_mon} {now.tm_mday} {item_time}", '%Y %m %d %H:%M')
                    schedule_times.append(new_time)
                schedule_times.sort()

                next_profile_change = None
                if schedule_times:
                    # find first time that would be the next event
                    for times in schedule_times:
                        if times > now:
                            break
                        next_profile_change = times

                if next_profile_change:
                    # get the original key again
                    schedule_index = f"{next_profile_change[3]}:{str(next_profile_change[4]).zfill(2)}"
                    # if the active profile is already the pending profile, then return none.
                    if hf.get_active_profile() == schedule[schedule_index]:
                        return None
                    else:
                        schedule_index = f"{next_profile_change[3]}:{str(next_profile_change[4]).zfill(2)}"
                        return schedule_index
                else:
                    return None
            else:
                return None

        next_profile = get_pending_profile_change()
        if next_profile:
            vote_data = hf.get_vote_data()
            if hf.set_active_profile(vote_data["Active Profile Schedule"][next_profile]):
                logging.info(f"[Voting] Switched profile to {hf.get_active_profile()}")
            else:
                logging.info(f"[Voting] Failed to switch profile: Profile does not exist.")

        voters_on_cooldown = hf.get_users_on_cooldown()
        data = hf.get_vote_data()
        voters_to_resolve = []

        # build a list of voters who have passed the cooldown.
        for voter in voters_on_cooldown:
            if data['Users On Cooldown'][voter]["cooldown end"] < time.time():
                voters_to_resolve.append(voter)

        if voters_to_resolve:
            logging.info(f"[Voting] Voters to be resolved: {voters_to_resolve}")

            # applies the votes and resets the cooldowns
            for voter in voters_to_resolve:
                amount = data["Users On Cooldown"][voter]["amount"]
                target = data["Users On Cooldown"][voter]["target"]
                profile = data["Users On Cooldown"][voter]["profile"]
                try:
                    amount = await self.apply_vote(target, voter, amount, profile)
                except OutOfLogsException as e:
                    if self.bots:
                        for bot in self.bots:
                            await bot.send_message(f"{voter} has run out of logs.")
                        hf.remove_user_from_cooldown(voter)
                        continue
                # resets the time for the next cooldown
                cooldown = hf.get_dynamic_cooldown_amount(max_vote_rate)
                if amount != "all" and amount < max_vote_rate:
                    cooldown = hf.get_dynamic_cooldown_amount(amount)
                hf.add_user_to_cooldown(voter, time.time() + cooldown, target, amount)

    async def remove_users_from_cooldown(self):
        users_on_cooldown = hf.get_users_on_cooldown()
        vote_data = hf.get_vote_data()

        for user in users_on_cooldown:
            user_data = vote_data["Users On Cooldown"][user]
            now = time.time()
            if user_data["cooldown end"] < now and user_data["amount"] <= 0:
                hf.remove_user_from_cooldown(user)

    async def decay(self):
        seconds_in_a_day = 86400
        decay_threshold = decay_days

        last_decay = 0
        if "Last Decay" in hf.get_vote_data().keys():
            last_decay = hf.get_vote_data()["Last Decay"]
        else:
            vote_data = hf.get_vote_data()
            vote_data["Last Decay"] = time.time()
            hf.update_vote_data(vote_data)

        # if it's time to decay again
        if time.time() - last_decay > seconds_in_a_day:
            vote_data = hf.get_vote_data()

            no_decay = []
            if "No Decay" in vote_data.keys():
                no_decay = vote_data["No Decay"]

            for profile in vote_data["Profiles"].keys():

                # skip this profile if it's in the no_decay list
                if profile in no_decay:
                    continue

                decay_threshold = hf.get_shield_count()
                possible_votes = list(vote_data["Profiles"][profile].keys())
                for vote in possible_votes:
                    elapsed_time = time.time() - vote_data["Profiles"][profile][vote]["last added"]

                    if elapsed_time > (seconds_in_a_day * decay_threshold):

                        days_past_threshold = int((elapsed_time - (seconds_in_a_day * decay_threshold)) / seconds_in_a_day)
                        decay_total = int(decay_amount) * days_past_threshold

                        new_value = vote_data["Profiles"][profile][vote]["vote value"] - decay_total

                        vote_data["Profiles"][profile][vote]["vote value"] = new_value

                        logging.info(f"[Voting] Decaying {profile}: {vote} by {decay_total}")

                        # checks if the value is less than 0 and corrects it.
                        if vote_data["Profiles"][profile][vote]["vote value"] < 0:
                            vote_data["Profiles"][profile][vote]["vote value"] = 0

                            if hf.get_active_profile() != "decayed":
                                # move it to the stone of stories after it runs out of
                                if "decayed" not in vote_data["Profiles"].keys():
                                    vote_data["Profiles"]["decayed"] = {}
                                vote_data["Profiles"]["decayed"][vote] = vote_data["Profiles"][profile][vote]
                                del vote_data["Profiles"][profile][vote]

            vote_data["Last Decay"] = time.time()
            hf.update_vote_data(vote_data)

    def stop_voting(self, user):
        """
        Sets the user's remaining amount to 0 and sets the cooldown based on the remaining amount.
        :param user: The user to bew removed
        :return:
        """
        data = hf.get_vote_data()

        if user in hf.get_users_on_cooldown():
            remaining_vote = 0
            user_cooldown_vote_value = data["Users On Cooldown"][user]["amount"]
            if user_cooldown_vote_value != "all":
                if user_cooldown_vote_value <= max_vote_rate:
                    remaining_vote = data["Users On Cooldown"][user]["amount"]
                else:
                    remaining_vote = max_vote_rate
            else:
                remaining_vote = max_vote_rate
            remaining_cooldown = hf.get_dynamic_cooldown_amount(remaining_vote)
            now = time.time()
            new_cooldown = now + remaining_cooldown
            data["Users On Cooldown"][user]["cooldown end"] = new_cooldown
            data["Users On Cooldown"][user]["amount"] = 0

        hf.update_vote_data(data)