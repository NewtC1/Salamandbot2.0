import asyncio
import os
import toml
import logging
import time
from utils import helper_functions as hf

settings = toml.load(os.path.join(os.path.dirname(__file__), "..\\utils\\settings.toml"))
base_cooldown = settings['settings']['cooldown_time']


class OutOfLogsException(Exception):
    pass


class VoteObject:

    def __init__(self, voter, amount, target):
        hf.add_active_voter(voter)
        self.voter = voter
        self.amount = amount
        self.target = target

    async def apply_vote(self):
        max_vote_rate = settings['settings']['max_vote_rate']
        amount_to_increase = max_vote_rate if self.amount > max_vote_rate else self.amount

        if hf.get_log_count(self.voter) < amount_to_increase:
            hf.remove_active_voter(self.voter)
            raise OutOfLogsException

        hf.set_vote_option_value(self.target, hf.get_vote_option_value(self.target) + amount_to_increase)
        hf.add_vote_contributor(self.target, self.voter, amount_to_increase)
        hf.set_log_count(self.voter, hf.get_log_count(self.voter) - amount_to_increase)

        self.amount = self.amount - amount_to_increase

        return self if self.amount > 0 else None


class VoteManager:

    def __init__(self, logger, votes = None):
        self.vote_list = {}
        if votes:
            self.vote_list = votes
        self.logger = logger

    def add_vote(self, vote: VoteObject):
        logging.info(f"[Voting] Adding vote: {vote.voter} voting {vote.amount} for {vote.target}")
        self.vote_list[vote.voter] = vote

    async def tick_vote(self):
        active_voters = hf.get_active_voters()
        data = hf.get_vote_data()
        voters_to_resolve = []

        # build a list of voters who have passed the cooldown.
        for voter in active_voters.keys():
            if data['Active Voters'][voter] < time.time() - base_cooldown:
                voters_to_resolve.append(voter)

        if voters_to_resolve:
            logging.info(f"[Voting] Voters to be resolved: {voters_to_resolve}")

            # applies the votes and resets the cooldowns
            for voter in voters_to_resolve:
                if voter not in self.vote_list.keys():
                    hf.remove_active_voter(voter)
                self.vote_list[voter] = await self.vote_list[voter].apply_vote()
                if not self.vote_list[voter]:
                    del self.vote_list[voter]
                    hf.remove_active_voter(voter)
                else:
                    # resets the time for the next cooldown
                    hf.add_active_voter(voter)

    async def cleanup(self):
        """
        Cleans up the voter list every 10 minutes.
        :return:
        """
        active_voters = hf.get_active_voters()

        for voter in self.vote_list.keys():
            if voter not in active_voters:
                del self.vote_list[voter]