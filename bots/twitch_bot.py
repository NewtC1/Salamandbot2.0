# twitch_bot.py
import asyncio
import os  # for importing env vars for the bot to use
import requests

import utils.helper_functions as hf
from twitchio.ext import commands

from utils.helper_functions import client_id


class TwitchBot(commands.bot.Bot):

    bot_startup = f"/me opens its eyes and rolls over. It awaits commands."

    def __init__(self, parser, loop: asyncio.BaseEventLoop=None, initial_channels=[os.environ['CHANNEL']]):
        super().__init__(
            # set up the bot
            client_id=os.environ['CLIENT_ID'],
            client_secret=os.environ['CLIENT_SECRET_TWITCH'],
            bot_id=os.environ['BOT_ID_TWITCH'],
            owner_id=os.environ['OWNER_ID_TWITCH'],
            prefix=os.environ['BOT_PREFIX'],
            # webhook_server=False,
            # local_host="localhost",
            # port=8080,
            # port=8080,
        )
        self.parser = parser
        self.parser.add_bot(self)
        self.bot_ready = False

        self.headers = {
            'client-id': client_id,
            'Authorization': f'Bearer {hf.irc_token}'
        }
        self.channel_id = requests.get(f"https://api.twitch.tv/helix/users?login={hf.target_channel}", headers=self.headers).json()['data'][0]['id']
        self.channel_obj = None

    async def event_ready(self):
        """Called once the bot goes online."""
        print(f"{os.environ['BOT_NICK']} opens its eyes, ready to accept commands!")
        self.bot_ready = True

    async def event_message(self, ctx):
        """Runs every time a message is sent in chat."""

        # make sure the bot ignores itself
        if not ctx.author:
            return

        await ctx.channel.send(self.parser.parse_input("twitch", ctx))

        return

    async def send_message(self, message):
        if self.bot_ready:
            # await self.join_channels(self.initial_channels)
            for channel in self.connected_channels:
                await channel.send(f"{message}")
        else:
            await asyncio.sleep(1)

    async def get_chatters(self, channel_name):
        await self.wait_for_ready()
        channels = await self.fetch_channels([self.channel_id])
        channel = self.get_channel(channel_name)
        if channel:
            chatter_list = []
            for chatter in channel.chatters:
                if not any(x in chatter.name for x in ['.']):
                    chatter_list.append(chatter.name)
            return chatter_list
        return


    async def is_live(self) -> bool:
        """
        Returns if the reciever channel is live or not.
        :return:
        """

        response = requests.get(f"https://api.twitch.tv/helix/streams?user_id={self.channel_id}", headers=self.headers)
        if response.status_code == requests.codes.ok:
            if response.json()["data"]:
                is_live = True
            else:
                is_live = False
        else: is_live = False

        return is_live
