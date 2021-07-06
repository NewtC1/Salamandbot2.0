# twitch_bot.py
import asyncio
import os  # for importing env vars for the bot to use
import requests
from twitchio.ext import commands


class TwitchBot(commands.bot.Bot):

    bot_startup = f"/me opens its eyes and rolls over. It awaits commands."

    def __init__(self, parser, loop: asyncio.BaseEventLoop=None):
        self.initial_channels = [os.environ['CHANNEL']]
        super().__init__(
            # set up the bot
            irc_token=os.environ['TMI_TOKEN'],
            client_id=os.environ['CLIENT_ID'],
            nick=os.environ['BOT_NICK'],
            prefix=os.environ['BOT_PREFIX'],
            initial_channels=self.initial_channels,
            loop=loop,
            # webhook_server=False,
            # local_host="localhost",
            # port=8080,
            # port=8080,
        )
        self.parser = parser
        self.bot_ready = False

    async def event_ready(self):
        """Called once the bot goes online."""
        print(f"{os.environ['BOT_NICK']} opens its eyes, ready to accept commands!")
        ws = self._ws  # this is only needed to send messages within event_ready
        await ws.send_privmsg(os.environ['CHANNEL'], self.bot_startup)
        self.bot_ready = True

    async def event_message(self, ctx):
        """Runs every time a message is sent in chat."""

        # make sure the bot ignores itself
        if ctx.author.name.lower() == os.environ['BOT_NICK'].lower():
            return

        await ctx.channel.send(self.parser.parse_input("twitch", ctx))

        return

    async def send_message(self, message):
        if self.bot_ready:
            # await self.join_channels(self.initial_channels)
            for channel in self.initial_channels:
                receiver_channel = self.get_channel(channel)
                await receiver_channel.send(message)
        else:
            await asyncio.sleep(1)

    async def is_live(self) -> bool:
        """
        Returns if the reciever channel is live or not.
        :return:
        """
        client_id = os.environ['CLIENT_ID']
        client_secret = os.environ["CLIENTSECRET"]
        target_channel = os.environ["CHANNEL"]

        oauth_request = requests.post(
            f"https://id.twitch.tv/oauth2/token?client_id={client_id}&client_secret={client_secret}&grant_type=client_credentials")
        irc_token = oauth_request.json()['access_token']

        headers = {
            'client-id': client_id,
            'Authorization': f'Bearer {irc_token}'
        }
        target_user = requests.get(f"https://api.twitch.tv/helix/users?login={target_channel}", headers=headers).json()['data'][0]['id']
        response = requests.get(f"https://api.twitch.tv/helix/streams?user_id={target_user}", headers=headers)
        if response.json()["data"]:
            is_live = True
        else:
            is_live = False

        return is_live

    async def chat_is_active(self) -> bool:
        response = requests.get("https://tmi.twitch.tv/group/user/newtc/chatters")
        return len(response.json()["chatters"]["viewers"]) > 0

