import logging
import json
import time
import random
import queue
from itertools import repeat
from utils import helper_functions as hf

rimeheart_dir = hf.settings["directories"]["rimeheart_giveaway"]
accounts_dir = hf.accounts_file


class RimeheartManager:
    def __init__(self, raffle_cost: int=hf.settings["events"]["raffle_cost"]):
        self.delay = hf.settings["events"]["rimeheart_delay"]
        self.next_vote = time.time() + self.delay
        self.raffle_list = []
        self.raffle_cost = raffle_cost
        data = self.load_rimeheart_data()
        self.current_game = list(data["valid_codes"].keys())[0] if len(data["valid_codes"].keys()) > 0 else "Pending"
        logging.info(f"[Rimeheart] Setting {self.current_game} as the current game.")

    def tick(self):
        output = ""

        if time.time() > self.next_vote:
            logging.info("[Rimeheart] Rolling a raffle.")
            self.next_vote = time.time() + self.delay

            winner = self.roll_raffle()

            if winner:
                logging.info(f"[Rimeheart] {winner} won the codes for {self.current_game}")

                # remove the game from the list
                data = self.load_rimeheart_data()
                data["invalid_codes"][self.current_game] = data["valid_codes"][self.current_game]
                codes = data['valid_codes'][self.current_game]
                del data["valid_codes"][self.current_game]
                self.update_rimeheart_data(data)
                logging.info(f"[Rimeheart] {winner} won the following codes: {codes}")
                output += f"Cicero hands the glowing packet of light to {winner}. Keep hold of that. Don't let it " \
                       f"go."
            else:
                data = self.load_rimeheart_data()
                data["skipped_codes"][self.current_game] = data["valid_codes"][self.current_game]
                del data["valid_codes"][self.current_game]
                self.update_rimeheart_data(data)
                logging.info(f"[Rimeheart] Moving {self.current_game} to skipped.")
                output += f"Cicero croons quietly and puts the strange object back in his bag, pulling out " \
                       f"something new."

            new_game = self.select_new_game()
            output += f" The object Cicero pulls out has a tag on it: {new_game}."
            self.current_game = new_game

        return output

    def load_rimeheart_data(self):
        with open(rimeheart_dir, encoding="utf-8-sig") as file_input:
            data = json.load(file_input)
        return data

    def update_rimeheart_data(self, new_data: dict):
        with open(rimeheart_dir, mode='w', encoding='utf-8-sig') as file_input:
            json.dump(new_data, file_input, indent="\t")

    def select_new_game(self):
        data = self.load_rimeheart_data()
        if not data['valid_codes'].keys():
            self.reset_skipped_codes()
            data = self.load_rimeheart_data()
        option_list = list(data["valid_codes"].keys())
        new_game = random.choice(option_list)
        logging.info(f"[Rimeheart] Selecting {new_game} as the next raffle target.")
        return new_game

    def buy_raffle(self, user):
        if hf.get_woodchip_count(user) > self.raffle_cost:
            hf.set_woodchip_count(user, hf.get_woodchip_count(user) - self.raffle_cost)
            self.raffle_list.append(user)
            return f"{user} has purchased a raffle for {self.current_game}."
        else:
            return "You don't have enough woodchips to purchase that."

    def buy_multiple_raffles(self, user, amount):
        if hf.get_woodchip_count(user) > self.raffle_cost*amount:
            hf.set_woodchip_count(user, hf.get_woodchip_count(user) - self.raffle_cost*amount)
            self.raffle_list.extend(repeat(user, amount))
            return f"{user} has purchased {amount} raffles for {self.current_game}."
        else:
            return "You don't have enough woodchips to purchase that."

    def roll_raffle(self):
        if self.raffle_list:
            choice = random.choice(self.raffle_list)
            self.raffle_list = []
            return choice
        else:
            return None

    def reset_skipped_codes(self):
        data = self.load_rimeheart_data()
        data["valid_codes"] = data["skipped_codes"]
        del data["skipped_codes"]
        self.update_rimeheart_data(data)
