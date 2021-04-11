# twitch_bot.py
import os  # for importing env vars for the bot to use
from twitchio.ext import commands

# @bot.command(name='test')
# async def test(ctx):
    # await ctx.send('test passed!')


class TwitchBot(commands.bot.Bot):

    bot_startup = f"/me opens its eyes and rolls over. It awaits commands."

    def __init__(self, parser):
        super().__init__(
            # set up the bot
            irc_token=os.environ['TMI_TOKEN'],
            client_id=os.environ['CLIENT_ID'],
            nick=os.environ['BOT_NICK'],
            prefix=os.environ['BOT_PREFIX'],
            initial_channels=[os.environ['CHANNEL']]
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
