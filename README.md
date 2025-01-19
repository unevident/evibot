A discord bot that starts listening for messages from a specific user in a specific channel, then uses eSpeak and MBROLA to vocalise the messages in the voice channel that the user is in. User must be muted to invoke the command ".listen".

The bot automatically times out if the user has not sent a message in 1000s. The bot will also not vocalise messages if they:
1. are more than 300 characters long (for sanity of other users in the voice channel)
2. contain links "https://" or "http://"
3. start with '.'

Commands:

.listen - Bot will begin listening to the specific user in that specific channel where the command was used. User must be muted by self at the time of using the command. 

.stop - Bot will stop listening to the specific user in that specific channel. Only works if the command was used in the channel where .listen was originally used.

Setting Commands:

(Note: using any of the below commands on their own with no further input will return the current value for that setting)

.changevoicelang - Changes the Voice language used in the voxpopuli voice used to vocalise messages. Requires that the host install MBROLA languages on their system.

.changevoiceid - Changes the Voice ID used in the voxpopuli voice for the currently used language. Requires that the host install MBROLA voices on their system.

.changespeed - Changes the words-per-min speed that the Voice recording is played at. Default: 140(wpm)

.changevolume - Changes the Voice's volume. Maximum: 3

.changepitch - Changes the Voice's pitch. Range: 0-99 inclusive.

Dependencies:

[eSpeak](https://espeak.sourceforge.net/) <- must be apt installed on your system with ```sudo apt-get install espeak```

[MBROLA](https://github.com/numediart/MBROLA) <- must also be apt installed on system with ```sudo apt-get install mbrola```

Note: MBROLA voices are not included. Please install them with apt. Recommended voices: mbrola-us2 mbrola-us3
Some installation instructions: (https://github.com/espeak-ng/espeak-ng/blob/master/docs/mbrola.md#linux-installation) 

[voxpopuli](https://voxpopuli.readthedocs.io/en/latest/install.html) <- There are no Windows/Mac installation instructions for this. I have no experience installing this outside of Linux

[ffmpeg](https://phoenixnap.com/kb/install-ffmpeg-ubuntu)

The other python library dependencies are in the requirements.txt

Note: If you pull this repo, you must create a .env file in the directory and put the "DISCORD_TOKEN=YOUR_DISCORD_BOT_TOKEN_HERE" for your bot to log into discord