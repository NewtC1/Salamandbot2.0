# twitch_bot.py
import asyncio
import json
import logging
import os  # for importing env vars for the bot to use
import asqlite
import twitchio

from typing import Any, TYPE_CHECKING
from twitchio.authentication import ValidateTokenPayload
from twitchio.ext import commands
from twitchio import eventsub, authentication

from input_parser import InputParser

if TYPE_CHECKING:
    import sqlite3

class TwitchBot(commands.AutoBot):

    bot_startup = f"/me opens its eyes and rolls over. It awaits commands."

    def __init__(self, parser, token_database: asqlite.Pool, subs: list[eventsub.SubscriptionPayload]):
        self.token_database = token_database

        super().__init__(
            # set up the bot
            client_id=os.environ['CLIENT_ID'],
            client_secret=os.environ['CLIENT_SECRET_TWITCH'],
            bot_id=os.environ['BOT_ID_TWITCH'],
            owner_id=os.environ['OWNER_ID_TWITCH'],
            prefix=os.environ['BOT_PREFIX']
        )

        # add the input parser and register this bot with it
        self.parser = parser
        self.parser.add_bot(self)
        self.bot_ready = False


    async def event_oauth_authorized(self, payload: authentication.UserTokenPayload) -> None:
        await self.add_token(payload.access_token, payload.refresh_token)

        if not payload.user_id:
            return

        if payload.user_id == self.bot_id:
            # We usually don't want subscribe to events on the bots channel...
            return

        # A list of subscriptions we would like to make to the newly authorized channel...
        subs: list[eventsub.SubscriptionPayload] = [
            eventsub.ChatMessageSubscription(broadcaster_user_id=payload.user_id, user_id=self.bot_id),
        ]

        resp: twitchio.MultiSubscribePayload = await self.multi_subscribe(subs)
        if resp.errors:
            logging.warning("Failed to subscribe to: %r, for user: %s", resp.errors, payload.user_id)


    async def add_token(self, token: str, refresh: str) -> twitchio.authentication.ValidateTokenPayload:
        # Make sure to call super() as it will add the tokens interally and return us some data...
        resp: twitchio.authentication.ValidateTokenPayload = await super().add_token(token, refresh)

        # Store our tokens in a simple SQLite Database when they are authorized...
        query = """
        INSERT INTO tokens (user_id, token, refresh)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id)
        DO UPDATE SET
            token = excluded.token,
            refresh = excluded.refresh;
        """

        async with self.token_database.acquire() as connection:
            await connection.execute(query, (resp.user_id, token, refresh))

        return resp


    async def setup_hook(self) -> None:
        with open(".tio.tokens.json", "rb") as fp:
            tokens = json.load(fp)

        for user_id in tokens:
            if user_id == self.bot_id:
                continue

            # Subscribe to chat for everyone we have a token...
            chat = eventsub.ChatMessageSubscription(broadcaster_user_id=user_id, user_id=self.bot_id)
            await self.subscribe_websocket(chat)

    async def event_ready(self):
        """Called once the bot goes online."""
        print(f"{os.environ['BOT_NICK']} opens its eyes, ready to accept commands!")
        self.bot_ready = True

    async def event_message(self, ctx):
        """Runs every time a message is sent in chat."""

        # make sure the bot ignores itself
        if ctx.chatter.name == os.environ["BOT_NICK"].lower():
            return

        user = self.create_partialuser(user_id=self.owner_id)
        await user.send_message(sender=self.user, message="Parsing...")
        # await user.send_message(sender=self.user, message=self.parser.parse_input("twitch", ctx))

        return

async def setup_database(db: asqlite.Pool) -> tuple[list[tuple[str, str]], list[eventsub.SubscriptionPayload]]:
    # Create our token table, if it doesn't exist..
    # You should add the created files to .gitignore or potentially store them somewhere safer
    # This is just for example purposes...

    query = """CREATE TABLE IF NOT EXISTS tokens(user_id TEXT PRIMARY KEY, token TEXT NOT NULL, refresh TEXT NOT NULL)"""
    async with db.acquire() as connection:
        await connection.execute(query)

        # Fetch any existing tokens...
        rows: list[sqlite3.Row] = await connection.fetchall("""SELECT * from tokens""")

        tokens: list[tuple[str, str]] = []
        subs: list[eventsub.SubscriptionPayload] = []

        for row in rows:
            tokens.append((row["token"], row["refresh"]))

            if row["user_id"] == os.environ['BOT_ID_TWITCH']:
                continue

            subs.extend([eventsub.ChatMessageSubscription(broadcaster_user_id=row["user_id"], user_id=os.environ['BOT_ID_TWITCH'])])

    return tokens, subs


def main() -> None:
    twitchio.utils.setup_logging(level=logging.INFO)

    async def runner() -> None:
        async with asqlite.create_pool("tokens.db") as tdb:
            tokens, subs = await setup_database(tdb)

            async with TwitchBot(token_database=tdb, subs=subs) as bot:
                for pair in tokens:
                    await bot.add_token(*pair)

                await bot.start(load_tokens=False)

