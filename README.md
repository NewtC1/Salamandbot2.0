# Salamandbot2.0
A twitch bot designed to connect multiple 3rd Party Platforms into one chat, while also allowing programming extensibility.

A couple of things to get started:
First, the bot needs a .env file at the root directory. Below is an example of one.

# .env
TMI_TOKEN=
CLIENT_ID=
BOT_NICK=
BOT_PREFIX=!
CHANNEL=
USERID=
CLIENTSECRET=
DISCORD_TOKEN=

Most of these names are self explanatory. TMI_TOKEN is the oauth token used to access the Twitch API. CLIENT_ID refers
to the ID of the bot. You will have to make one of these yourself on https://dev.twitch.tv/. BOT_NICK is the name of the
account the bot uses to interact with chat. BOT_PREFIX is actually unused, but TwitchIO likes to have it if development
is done with that. CHANNEL refers to the channel the bot will be watching for commands. USERID is in reference to the
channel's userID, and can be found through this request: GET https://api.twitch.tv/helix/users?login=<username>.

The last two variables refer to the bot's discord information. If you want to enable Discord usage, you'll need to set
up a Discord bot at https://discord.com/developers/applications.
