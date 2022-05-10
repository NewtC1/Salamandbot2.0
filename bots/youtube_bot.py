import asyncio
import os
import pickle

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


class YouTubeBot:

    api_service_name = "youtube"
    api_version = "v3"
    scopes = ["https://www.googleapis.com/auth/youtube", "https://www.googleapis.com/auth/youtube.force-ssl"]
    youtube_api_key = os.environ["YOUTUBE_API"]
    youtube_channel_id = os.environ["YOUTUBE_CHANNEL_ID"]

    maximum_polling_length = 120
    minimum_polling_length = 1

    def __init__(self, parser):
        self.client_secrets_file = 'youtube_secrets.json'

        self.streamer_youtube = self.create_youtube_object("streamer_token.pickle")
        self.bot_youtube = self.create_youtube_object("bot_token.pickle")

        self.last_live_chat = self.get_last_live_chat()
        self.live = False
        self.current_polling_interval = self.minimum_polling_length
        # ignore all chat messages from before the bot started.
        self.last_chat_message_count = self.get_last_chat_message_position(self.last_live_chat)

        self.parser = parser
        self.parser.add_bot(self)

    def create_youtube_object(self, pickle_token):
        if os.path.exists(os.path.join(os.getcwd(), pickle_token)):
            with open(pickle_token, "rb") as token:
                credentials = pickle.load(token)
        else:

            flow = InstalledAppFlow.from_client_secrets_file(self.client_secrets_file, self.scopes)
            credentials = flow.run_local_server(authorization_prompt_message="")

            with open(pickle_token, "wb") as f:
                print("Saving Credentials for Future Use...")
                pickle.dump(credentials, f)

        youtube = build(self.api_service_name, self.api_version, credentials=credentials)
        return youtube

    async def event_message(self, ctx):
        # make sure the bot ignores itself
        if ctx.author.name.lower() == os.environ['BOT_NICK'].lower():
            return

        await self.send_message(self.parser.parse_input("youtube", ctx))

        return

    async def send_message(self, message):
        if message:
            request = self.bot_youtube.liveChatMessages().insert(
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
        broadcasts = self.streamer_youtube.liveBroadcasts().list(
            part="snippet,status",
            broadcastStatus="active",
            broadcastType="all"
        )
        # should return any active broadcasts (but should never exceed more 1 broadcast)
        active_broadcasts = broadcasts.execute()
        if active_broadcasts["items"]:
            if active_broadcasts["items"][0]['snippet']['liveChatId'] != self.last_live_chat:
                self.last_live_chat = active_broadcasts["items"][0]['snippet']['liveChatId']
            self.live = True
            return True
        else:
            self.live = False
            return False

    def get_last_live_chat(self):
        broadcasts = self.streamer_youtube.liveBroadcasts().list(
            part="snippet,status",
            broadcastStatus="all",
            broadcastType="all"
        ).execute()
        return broadcasts["items"][0]['snippet']['liveChatId']

    @staticmethod
    def _convert_to_seconds(milliseconds: str):
        return float(milliseconds)/1000.0

    @staticmethod
    async def convert_to_ctx(message):
        author = Author(message['snippet']['authorChannelId'])
        content = message["snippet"]["displayMessage"]
        output = Message(author=author, content=content)
        return output

    async def _listen(self):
        """
        Listens for any new chat messages and sends them to the parser for response.
        :return:
        """
        while True:
            # if the YouTube channel is not live, then go into low-request mode
            if await self.is_live():
                chat_messages = self.streamer_youtube.liveChatMessages().list(
                    liveChatId=self.last_live_chat,
                    part="snippet",
                    maxResults=10000
                )
                response = chat_messages.execute()

                # if there aren't any new messages, then pass off handling events to something else.
                total_results = response["pageInfo"]["totalResults"]

                # backoff code
                if self.current_polling_interval * 2 < self.maximum_polling_length:
                    self.current_polling_interval = self.current_polling_interval * 2
                else:
                    self.current_polling_interval = self.maximum_polling_length

                # else, handle any waiting messages
                if total_results != self.last_chat_message_count:
                    for message in response["items"][self.last_chat_message_count: total_results]:
                        ctx = await self.convert_to_ctx(message)
                        await self.event_message(ctx)
                        self.last_chat_message_count += 1

                    self.current_polling_interval = self.minimum_polling_length

                # sleep until the next poll interval
                await asyncio.sleep(self.current_polling_interval)
            else:
                await asyncio.sleep(600)

    def get_last_chat_message_position(self, chat_id):
        chat_messages = self.streamer_youtube.liveChatMessages().list(
            liveChatId=chat_id,
            part="snippet"
        )

        if self.live:
            response = chat_messages.execute()
            return len(response['items'])
        else:
            return 0

    async def start(self):

        try:
            await self._listen()
        except KeyboardInterrupt:
            pass
        finally:
            self.streamer_youtube.close()
            self.bot_youtube.close()


# Data classes for youtube messages.
class YouTubeUser:
    __slots__ = ('_channel', '_display_name')

    def __init__(self, **attrs):
        pass


class Author:

    def __init__(self, name):
        self.name = name


class Message:

    def __init__(self, author: Author, content):
        self.author = author
        self.content = content
