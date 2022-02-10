# twitch_bot.py
import asyncio
import os  # for importing env vars for the bot to use

from discord.client import Client


class DiscordBot(Client):

    bot_startup = f"/me opens its eyes and rolls over. It awaits commands."

    def __init__(self, parser, loop: asyncio.BaseEventLoop=None):
        self.initial_channels = [os.environ['CHANNEL']]
        super().__init__(
            # set up the bot
            command_prefix=os.environ['BOT_PREFIX'],
            loop=loop
        )
        self.parser = parser
        self.bot_ready = False

    async def on_ready(self):
        """Called once the bot goes online."""
        print('We have logged in as {0.user}'.format(self))
        self.bot_ready = True

    async def on_message(self, ctx):
        """Runs every time a message is sent in chat."""

        # make sure the bot ignores itself
        if ctx.author.name.lower() == os.environ['BOT_NICK'].lower():
            return
        if ctx.channel.id != os.environ['DISCORD_BOT_CHANNEL_ID']:
            return

        parse_output = self.parser.parse_input("discord", ctx)
        if parse_output:
            await ctx.channel.send(parse_output)

        return

    async def send_message(self, message:str):
        if self.bot_ready:
            channel = self.get_channel(int(os.environ['DISCORD_BOT_CHANNEL_ID']))
            await channel.send(message)
        else:
            await asyncio.sleep(1)

    async def is_live(self) -> bool:
        """
        Discord bot is always considered live.
        :return:
        """
        return False