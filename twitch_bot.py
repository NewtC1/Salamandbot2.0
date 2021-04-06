# twitch_bot.py
import json
import logging
import os  # for importing env vars for the bot to use
from twitchio.ext import commands

bot = commands.Bot(
    # set up the bot
    irc_token=os.environ['TMI_TOKEN'],
    client_id=os.environ['CLIENT_ID'],
    nick=os.environ['BOT_NICK'],
    prefix=os.environ['BOT_PREFIX'],
    initial_channels=[os.environ['CHANNEL']]
)

bot_startup = f"/me opens its eyes and rolls over. It awaits commands."


@bot.event
async def event_ready():
    """Called once the bot goes online."""
    print(f"{os.environ['BOT_NICK']} is opens its eyes, ready to accept commands!")
    ws = bot._ws  # this is only needed to send messages within event_ready
    await ws.send_privmsg(os.environ['CHANNEL'], bot_startup)


@bot.event
async def event_message(ctx):
    """Runs every time a message is sent in chat."""

    # make sure the bot ignores itself
    if ctx.author.name.lower() == os.environ['BOT_NICK'].lower():
        return

    await bot.handle_commands(ctx)

    greeting = lambda a: a in ctx.content.lower()
    greeting_search_results = [greeting("heya"), greeting("hello"), greeting("bonjour")]
    if any(greeting_search_results):
        await ctx.channel.send(f"Welcome to the campgrounds, @{ctx.author.name}!")

    return


@bot.command(name='test')
async def test(ctx):
    await ctx.send('test passed!')


# twitch_bot.py
if __name__ == "__main__":
    bot.run()
