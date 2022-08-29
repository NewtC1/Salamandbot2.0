# twitch_bot.py
import asyncio
import os  # for importing env vars for the bot to use
import utils.helper_functions as hf

import discord
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
        self.current_voice_client = None

    async def on_ready(self):
        """Called once the bot goes online."""
        print('We have logged in as {0.user}'.format(self))
        self.bot_ready = True

    async def on_message(self, ctx):
        """Runs every time a message is sent in chat."""

        length_of_content = len(ctx.content)
        if len(ctx.content) > 40:
            hf.set_log_count(ctx.author, hf.get_log_count(ctx.author) + int(length_of_content/40))

        # make sure the bot ignores itself
        if ctx.author.name.lower() == os.environ['BOT_NICK'].lower():
            return
        if not isinstance(ctx.channel, discord.DMChannel):
            if ctx.channel.name != os.environ['DISCORD_BOT_CHANNEL']:
                return
        if not ctx.content.startswith("!"):
            return

        # checks first to see if there's a matching sound file
        first_word = ctx.content.strip("!")
        sfx_list = os.listdir(hf.sfx_file)
        index = None
        for sfx in sfx_list:
            if first_word == sfx.split(".")[0]:
                index = sfx_list.index(sfx)
                break

        # if there's a sound file have the Discord bot handled it.
        if isinstance(index, int):
            sfx_file_path = os.path.join(hf.sfx_file, sfx_list[index])
            await self.play_audio(ctx.author, sfx_file_path)
            return

        # else, send it to the parser
        parse_output = self.parser.parse_input("discord", ctx)
        if parse_output:
            if "!discord" in parse_output:
                if "join" in parse_output:
                    await self.join_voice(ctx.author)
                elif "leave" in parse_output:
                    await self.leave_voice()
                elif "play" in parse_output:
                    source = parse_output.split()[-1]
                    await self.play_audio(ctx.author, source)
            else:
                await ctx.channel.send(parse_output)

        return

    async def on_voice_state_update(self, member:discord.Member, before:discord.VoiceClient, after:discord.VoiceClient):
        if member.display_name == "John Cena" and after.channel and before.channel != after.channel:
            await self.play_audio(member, "sounds/john_cena.mp3")

    async def send_message(self, message:str):
        if self.bot_ready:
            channel = self.get_channel(int(os.environ['DISCORD_BOT_CHANNEL_ID']))
            await channel.send(message)
        else:
            await asyncio.sleep(1)

    async def join_voice(self, instigating_member:discord.Member):
        # join the channel
        channel_to_join = instigating_member.voice.channel

        if channel_to_join:
            voice_client = await channel_to_join.connect()
            self.current_voice_client = voice_client
        else:
            await self.send_message(f"{instigating_member} is not in a voice channel. "
                                    f"Join the channel you want Salamandbot to join.")

    async def leave_voice(self):
        if self.current_voice_client:
            await self.current_voice_client.voice_disconnect()
            self.current_voice_client = None
        else:
            await self.send_message(f"Salamandbot is not in a voice channel.")

    async def play_audio(self, member, source_file):
        await self.join_voice(member)
        audio_source = discord.FFmpegPCMAudio(source_file)
        self.current_voice_client.play(audio_source)
        while self.current_voice_client.is_playing():
            await asyncio.sleep(1)
        await self.leave_voice()

    async def is_live(self) -> bool:
        """
        Discord bot is always considered live.
        :return:
        """
        return False