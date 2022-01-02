import asyncio
import os
import pickle

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from twitchio.dataclasses import User

class YouTubeBot:

    api_service_name = "youtube"
    api_version = "v3"
    scopes = ["https://www.googleapis.com/auth/youtube", "https://www.googleapis.com/auth/youtube.force-ssl"]
    youtube_api_key = os.environ["YOUTUBE_API"]
    youtube_channel_id = os.environ["YOUTUBE_CHANNEL_ID"]

    def __init__(self, parser):
        self.client_secrets_file = 'youtube_secrets.json'
        self.credentials = None

        if os.path.exists(os.path.join(os.getcwd(), "token.pickle")):
            with open("token.pickle", "rb") as token:
                self.credentials = pickle.load(token)
        else:

            self.flow = InstalledAppFlow.from_client_secrets_file(self.client_secrets_file, self.scopes)
            self.credentials = self.flow.run_local_server(authorization_prompt_message="")

            with open("token.pickle", "wb") as f:
                print("Saving Credentials for Future Use...")
                pickle.dump(self.credentials, f)

        self.youtube = build(self.api_service_name, self.api_version, credentials=self.credentials)
        self.last_live_chat = self.get_last_live_chat()
        self.last_chat_message_count = 0

        self.parser = parser

    async def event_ready(self):
        pass

    async def event_message(self, ctx):
        # make sure the bot ignores itself
        if ctx.author.name.lower() == os.environ['BOT_NICK'].lower():
            return

        await ctx.channel.send(self.parser.parse_input("youtube", ctx))

        return

    async def send_message(self, message):
        request = self.youtube.liveChatMessages().insert(
            part="snippet",
            body={
                "snippet": {
                    "liveChatId": self.last_live_chat,
                    "type": "textMessageEvent",
                    "textMessageDetails": {
                        "messageText": message
                    }
                }
            }
        )

        response = request.execute()
        return response

    async def is_live(self) -> bool:
        broadcasts = self.youtube.liveBroadcasts().list(
            part="snippet,status",
            broadcastStatus="active",
            broadcastType="all"
        )
        # should return any active broadcasts (but should never exceed more 1 broadcast)
        active_broadcasts = broadcasts.execute()
        if active_broadcasts["items"]:
            return True
        else:
            return False

    def get_last_live_chat(self):
        broadcasts = self.youtube.liveBroadcasts().list(
            part="snippet,status",
            broadcastStatus="all",
            broadcastType="all"
        ).execute()
        return broadcasts["items"][0]['snippet']['liveChatId']

    async def _listen(self):
        """
        Listens for any new chat messages and sends them to the parser for response.
        :return:
        """
        while True:
            # if the YouTube channel is not live, then go into low-request mode
            if await self.is_live() == True:
                chat_messages = self.youtube.liveChatMessages().list(
                    liveChatId=self.last_live_chat,
                    part="snippet"
                )
                response = chat_messages.execute()

                # if there aren't any new messages, then pass off handling events to something else.
                total_results = response["pageInfo"]["totalResults"]
                if total_results == self.last_chat_message_count:
                    await asyncio.sleep(1)
                else:
                    for message in response["items"][self.last_chat_message_count, response["pageInfo"]["totalResults"]]:
                        ctx = await self.convert_to_ctx(message)
                        # await self.event_message(ctx)
                    self.last_chat_message_count = response["pageInfo"]["totalResults"]
            else:
                await asyncio.sleep(60)

    async def convert_to_ctx(self, message):
        author = message["authorDetails"]["channelID"],
        content = message["snippet"]["displayMessage"]
        output = Message(author=author, content=content)
        return output

    async def start(self):

        try:
            await self._listen()
        except KeyboardInterrupt:
            pass
        finally:
            self.youtube.close()


class YouTubeUser:
    __slots__ = ('_channel', '_display_name')

    def __init__(self, **attrs):
        pass


class Message:

    def __init__(self, author, content):
        pass