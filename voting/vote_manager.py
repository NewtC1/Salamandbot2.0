import asyncio
import os
import toml
import logging
from utils import helper_functions as hf

settings = toml.load(os.path.join(os.path.dirname(__file__), "..\\utils\\settings.toml"))


class VoteObject:

    def __init__(self, voter, amount, target):
        self.voter = voter
        self.amount = amount
        self.target = target

    async def apply_vote(self):
        max_vote_rate = settings['settings']['max_vote_rate']
        amount_to_reduce = max_vote_rate if self.amount > max_vote_rate else self.amount
        hf.set_vote_option_value(self.target, hf.get_vote_option_value(self.target) - amount_to_reduce)

        self.amount = self.amount - amount_to_reduce

        return self if self.amount > 0 else None


class VoteManager:

    def __init__(self, logger, votes: asyncio.Queue = None):
        self.vote_list = votes
        self.logger = logger

    async def add_vote(self, vote: VoteObject):
        self.vote_list.put_nowait(vote)

    async def tick_vote(self):
        vote_objects_to_readd = []

        while not self.vote_list.empty():
            vote_to_resolve = await self.vote_list.get()
            vote_after_applying = await vote_to_resolve.apply_vote()
            logging.info(f"[Vote] Applying {vote_to_resolve.voter} vote for {vote_to_resolve.target} of {vote_to_resolve.amount}.")
            if vote_after_applying:
                vote_objects_to_readd.append(vote_after_applying)

        logging.info(f"[Vote] Readding votes.")
        for vote in vote_objects_to_readd:
            await self.vote_list.put(vote)
