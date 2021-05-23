# twitch_bot.py
import asyncio
import os  # for importing env vars for the bot to use
import requests
from twitchio.ext import commands
from twitchAPI.twitch import Twitch


class TwitchBot(commands.bot.Bot):

    bot_startup = f"/me opens its eyes and rolls over. It awaits commands."

    def __init__(self, parser, loop: asyncio.BaseEventLoop=None):
        super().__init__(
            # set up the bot
            irc_token=os.environ['TMI_TOKEN'],
            client_id=os.environ['CLIENT_ID'],
            nick=os.environ['BOT_NICK'],
            prefix=os.environ['BOT_PREFIX'],
            initial_channels=[os.environ['CHANNEL']],
            loop=loop
        )
        self.parser = parser

    async def event_ready(self):
        """Called once the bot goes online."""
        print(f"{os.environ['BOT_NICK']} opens its eyes, ready to accept commands!")
        ws = self._ws  # this is only needed to send messages within event_ready
        await ws.send_privmsg(os.environ['CHANNEL'], self.bot_startup)

    async def event_message(self, ctx):
        """Runs every time a message is sent in chat."""

        # make sure the bot ignores itself
        if ctx.author.name.lower() == os.environ['BOT_NICK'].lower():
            return

        await ctx.channel.send(self.parser.parse_input("twitch", ctx))

        return

    def send_message(self, message):
        for channel in self.initial_channels:
            receiver_channel = self.get_channel(channel)
            loop = asyncio.get_event_loop()
            loop.create_task(receiver_channel.send(message))

    async def is_live(self) -> bool:
        """
        Returns if the reciever channel is live or not.
        :return:
        """
        # requests.get(f"https://api.twitch.tv/helix/streams?client_id=id&channel={self.initial_channels}")
        is_live = True

        for channel in self.initial_channels:
            reciever_channel = await self.get_stream(self.get_channel(channel))
            if not reciever_channel:
                is_live = False

        return is_live

    async def chat_is_active(self) -> bool:
        response = requests.get("https://tmi.twitch.tv/group/user/newtc/chatters")
        return len(response.json()["chatters"]["viewers"]) > 0
