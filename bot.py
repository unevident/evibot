import os
import asyncio
import re
from io import BytesIO
import yt_dlp

import discord
from discord.ext import commands
from dotenv import load_dotenv

from voxpopuli import Voice


description = '''Example bot'''

intents = discord.Intents.default()
intents.message_content = True

currentListener = None
currentlyListening = False
currentlyPlaying = False
voiceChannel = None
currentlyPaused = False

yt_dl_options = {"format": "bestaudio/best"}

ytdl = yt_dlp.YoutubeDL(yt_dl_options)

ffmpeg_options = {'options': '-vn', 'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'}

voice = Voice(lang="us", speed=140, voice_id=2)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix = '.', description=description, intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} with ID {bot.user.id} has connected to Discord')
    global voice
    # The following commented code creates a test.wav file in bot.py's directory that plays when the bot joins a voice chat.
    # testwav = voice.to_audio("Ready to listen.")
    # with open("test.wav", "wb") as testwrite:
    #     testwrite.write(testwav)

@bot.command()
async def listen(ctx:commands.Context):
    global currentListener
    global currentlyListening
    global currentlyPlaying
    """Starts listening for messages from the command invoker in the channel where the command was invoked. If invoker is muted in voice chat and sends non-link messages below 300 characters, 
    the bot will send a TTS message with that content. If no messages are sent by the member in 1000s, or the user sends .stop, the bot stops listening."""
    if currentlyListening or currentListener != None and currentListener != ctx.author:
        return await ctx.send(f'Sorry, the bot is currently listening to {currentListener}')
    if ctx.author.voice == None:
        return await ctx.send('You must be in a voice channel to use this command.')
    if ctx.author.voice.self_mute == False:
        return await ctx.send('You must be muted in the voice channel to use this command.')
    await ctx.send(f'Now listening for messages from {ctx.author} in {ctx.message.channel}.')

    currentlyListening = True
    currentListener = ctx.author
    # The check logic for message (must be legal message, in correct channel, from correct user, < 300 characters, does not contain link, does not start with "-")
    def check(message: discord.Message):
        return message.content is not None \
            and message.channel == ctx.channel \
            and message.author == currentListener \
            and message.author == ctx.author \
            and len(message.content) < 300 \
            and not (message.content.__contains__("https://") or message.content.__contains__("http://") or message.content.startswith(".") or  "-" in message.content)
    
    global voiceChannel
    voiceChannel = await ctx.author.voice.channel.connect()
    currentlyPlaying = True
    # Defined in listen function. Sets currentlyPlaying to false after playing join message.
    def setCurrentlyPlayingFalse():
        global currentlyPlaying
        currentlyPlaying = False
    
    global voice
    twav = voice.to_audio("Ready to listen")
    with open("help.wav", mode="wb") as test: 
        test.write(twav);

    twavFileLike = BytesIO(twav)
    currentlyPlaying = True

    print(twavFileLike.getvalue)

    voiceChannel.play(discord.FFmpegPCMAudio(twavFileLike, pipe=True), after=lambda f: setCurrentlyPlayingFalse())

    # When valid message is received, if bot is listening, try to TTS
    while currentlyListening:
        try:
            voice_status = ctx.author.voice
            if not voice_status:
                return await ctx.send("Error: User not detected in voice channel")
            
            message = await bot.wait_for('message', check=check, timeout=1000)
                
            # If bot is currently playing an audio file, don't interrupt with another audio file
            if not currentlyPlaying:
                content = message.content
                searchEmote = re.search(r"(:\w+:)(\d+)", message.content)
                while searchEmote != None:
                    searchEmote = re.search(r"(:\w+:)(\d+)", content)
                    if searchEmote != None:
                        content = content[0:searchEmote.span()[0]] + searchEmote.group(1) + content[searchEmote.span()[1]:]

                wav = voice.to_audio(content)
                wavFileLike = BytesIO(wav)

                currentlyPlaying = True
                # finishPlay sets the currentlyPLaying variable to false to accept more messages. Also closes the wav file-like stream.
                def finishPlay():   
                    global currentlyPlaying
                    currentlyPlaying = False
                    wavFileLike.close()

                voiceChannel.play(discord.FFmpegPCMAudio(wavFileLike, pipe=True), after=lambda e: finishPlay())

            else:
                await ctx.send('Sorry, too many messages are being sent. Please wait until I have finished vocalizing my previous sentence.')

        except asyncio.TimeoutError as time:
            
            if (currentlyListening or (voiceChannel != None)):
                currentlyListening = False
                currentListener = None
                currentlyPlaying = False
                await ctx.send(f"Listening command timed out. {time}")
                await ctx.send("https://tenor.com/view/voice-little-mermaid-the-little-mermaid-stealing-your-voice-stealing-voice-gif-3727432")
                await voiceChannel.disconnect()
                voiceChannel = None

        except Exception as e:
            await ctx.send(f"Listen command stopped. Error: {e}")
            currentlyListening = False
            currentListener = None
            currentlyPlaying = False
            await voiceChannel.disconnect()
            voiceChannel = None

@bot.command()
async def stop(ctx:commands.Context):
    """If bot is currently listening for messages from a user, stops listening. Does nothing otherwise."""
    global currentlyListening
    global currentListener
    global currentlyPlaying
    global voiceChannel
    message = ctx.message
    if message.author == currentListener and voiceChannel != None and (currentlyListening or currentlyPlaying):
        await ctx.send(f"Stopped listening for messages from {message.author}")
        await ctx.send("https://tenor.com/view/voice-little-mermaid-the-little-mermaid-stealing-your-voice-stealing-voice-gif-3727432")
        currentListener = None
        currentlyListening = False
        currentlyPlaying = False
        await voiceChannel.disconnect()
        voiceChannel = None
    else:
        await ctx.send(f"Bot is currently not listening to {ctx.author}.")


@bot.command()
async def changevoicelang(ctx:commands.Context):
    """Changes the Voice's Language being used in the bot. Defaults to the base voiceID for the language chosen. (Please use changeVoiceID command to change voice ID)"""
    voiceList = Voice.list_voice_ids()

    global voice
    lang = voice.lang
    speed = voice.speed
    pitch = voice.pitch
    volume = voice.volume

    message = ctx.message.content
    if message == ".changevoicelang":
        output = ""
        for key in voiceList.keys():
            output += key
            output += ", "
        return await ctx.send(f"List of possible languages: {output}. Currently using: {lang}")
    
    message = message[16:]
    message = message.strip()
    if message in voiceList:
        voice = Voice(speed=speed, pitch=pitch, lang=message, volume=volume)
        return await ctx.send(f"Successfully changed Voice language to {message}. Currently using default Voice ID ({voice.voice_id}) for selected language.")
    
    return await ctx.send("Failed to change Voice language. Please ensure the language exists in my database.")

@bot.command()
async def changevoiceid(ctx:commands.Context):
    """Changes the Voice's ID being used for the bot's Voice. Does NOT change the language the Voice uses."""
    voiceList = Voice.list_voice_ids()
    global voice

    message = ctx.message.content

    voice_id = voice.voice_id
    lang = voice.lang
    speed = voice.speed
    pitch = voice.pitch
    volume = voice.volume
    if ctx.message.content == ".changevoiceid":
        output = ""
        for val in voiceList[lang]:
            output += val
            output += ", "
        return await ctx.send(f"List of possible Voice IDs: {output}. Currently using: {voice_id}")

    message = message[15:]
    message = message.strip()
    if message in voiceList[lang]:
        voice = Voice(speed=speed, pitch=pitch, lang=lang, volume=volume, voice_id=int(message))
        return await ctx.send(f"Successfully changed Voice ID to {message}.")
    
    return await ctx.send("Failed to change Voice ID. Please ensure the ID exists for the current Voice language.")

@bot.command()
async def changespeed(ctx:commands.Context):
    """Changes the speed of the Voice. Default and regular speed: 160 (words per minute)"""
    global voice
    message = ctx.message.content
    voice_id = voice.voice_id
    lang = voice.lang
    speed = voice.speed
    pitch = voice.pitch
    volume = voice.volume
    if message == ".changespeed":
        return await ctx.send(f"Current speed: {speed} (wpm)")
    message = message[12:]
    message = message.strip()
    try:
        val = int(message)
        voice = Voice(speed=val, pitch=pitch, lang=lang, voice_id=voice_id, volume=volume)
        return await ctx.send(f"Successfully set Voice speed to {message}.")

    except ValueError as e:
        return await ctx.send(f"Value entered is not a valid input. {e}")

@bot.command()
async def changepitch(ctx:commands.Context):
    """Changes the pitch of the Voice. Range: 0 - 99 inclusive."""
    global voice
    message = ctx.message.content
    voice_id = voice.voice_id
    lang = voice.lang
    speed = voice.speed
    pitch = voice.pitch
    volume = voice.volume
    if message == ".changepitch":
        return await ctx.send(f"Current pitch: {pitch}")
    message = message[12:]
    message = message.strip()
    try:
        val = int(message)
        voice = Voice(speed=speed, pitch=val, lang=lang, voice_id = voice_id, volume=volume)
        return await ctx.send(f"Successfully set Voice pitch to {message}.")
    except ValueError as e:
        return await ctx.send(f"Value entered is not a valid input. {e}")
    
@bot.command()
async def changevolume(ctx:commands.Context):
    """Changes the volume of the Voice. A float ratio (decimals ok) applied to the Voice .wav. Defaults to 1. Maximum: 3"""
    global voice
    message = ctx.message.content
    voice_id = voice.voice_id
    lang = voice.lang
    speed = voice.speed
    pitch = voice.pitch
    volume = voice.volume
    if message == ".changevolume":
        return await ctx.send(f"Current volume: {volume}")
    message = message[13:]
    message = message.strip()
    try:
        val = float(message)
        if val <= 3.0:
            voice = Voice(speed=speed, pitch=pitch, lang=lang, voice_id=voice_id, volume=val)
            return await ctx.send(f"Successfully set Voice volume to {message}.")
        raise ValueError('Value is too high. Maximum is 3.0.')
    
    except ValueError as e:
        return await ctx.send(f"Value entered is not a valid input. {e}")
    
@bot.command()
async def debuginfo(ctx:commands.Context):
    """Debug information about the bot for bug-fixing."""
    global currentListener
    global currentlyListening
    global currentlyPlaying
    global voiceChannel
    return await ctx.send(f"Current Listener: {currentListener} \nCurrently Listening? {currentlyListening} \nCurrently Playing? {currentlyPlaying} \nVoice Channel: {voiceChannel}")

@bot.command()
async def yt(ctx:commands.Context):
    """Tries to play the given url. Format: '.yt https://www.youtube.com/abcdef'"""
    global currentlyPlaying
    global voiceChannel

    def setCurrentlyPlayingFalse():
        global currentlyPlaying
        currentlyPlaying = False

    if currentlyPlaying:
        return await ctx.send(f"Sorry, I am currently playing something else.")
    
    try:
        if ctx.author.voice.channel == None:
            return await ctx.send(f"Unable to locate voice channel. Please use this command only while in a voice channel.")
    except Exception as e:
        print(e)
        return await ctx.send("Unable to locate voice channel. Please use this command only while in a voice channel.")

    if voiceChannel != None:    
        if ctx.author.voice.channel != voiceChannel.channel:
            try:
                voiceChannel = await ctx.author.voice.channel.connect()
            except Exception as e:
                print(e)
                await ctx.send("Unable to join voice channel from another channel. Please contact the bot owner")
    
    if voiceChannel == None:
        try:
            voiceChannel = await ctx.author.voice.channel.connect()
        except Exception as e:
            print(e)
            await ctx.send("Unable to join voice channel. Please contact the bot owner")
    
    try:
        message = ctx.message.content
        url = message.split()[1]
    except Exception as e:
        print(e)
        return await ctx.send("Unable to parse url sent with the .yt command.")

    if url[12:19] != "youtube":
        if url[8:16] != "youtu.be":
            return await ctx.send("Unable to recognize url as valid youtube link.")

    try:
        data = ytdl.extract_info(url, download=False)
        song = data['url']
        await ctx.send("Now playing: " + data["title"])
    except Exception as e:
        print(e)
        return await ctx.send("Failed to obtain valid JSON response from ytdl query")

    try:
        currentlyPlaying = True
        player = discord.FFmpegPCMAudio(song, **ffmpeg_options)
        voiceChannel.play(player, after=lambda f: setCurrentlyPlayingFalse())
    except Exception as e:
        print(e)
        return await ctx.send("Unable to play ffmpeg file for some reason. Look at bot log output")
    
@bot.command()
async def ytpause(ctx:commands.context):
    """Pauses the bot if it is currently playing."""
    global currentlyPlaying
    global currentlyPaused
    global voiceChannel

    if not voiceChannel:
        return await ctx.send("Bot is not in a voice channel.")
    if not currentlyPlaying:
        return await ctx.send("Unable to pause as there is nothing playing.")
    if currentlyPaused:
        return await ctx.send("Already paused.")
    currentlyPaused = True
    currentlyPlaying = False
    try:
        voiceChannel.pause()
        return await ctx.send("Paused the currently playing song.")
    except Exception as e:
        print(e)
        return await ctx.send("Encountered an issue while trying to pause. Check bot logs.")
    
@bot.command()
async def ytresume(ctx:commands.context):
    """Resumes the bot if it is currently paused."""
    global currentlyPlaying
    global currentlyPaused
    global voiceChannel

    if not voiceChannel:
        return await ctx.send("Bot is not in a voice channel.")
    if currentlyPlaying:
        return await ctx.send("Unable to resume as bot is already playing.")
    if not currentlyPaused:
        return await ctx.send("Already resumed.")
    currentlyPaused = False
    currentlyPlaying = True
    try:
        voiceChannel.resume()
        return await ctx.send("Resumed the currently playing song.")
    except Exception as e:
        print(e)
        return await ctx.send("Encountered an issue while trying to resume. Check bot logs.")
    
@bot.command()
async def ytstop(ctx:commands.context):
    """Stops the bot if it is currently playing."""
    global currentlyPlaying
    global currentlyPaused
    global voiceChannel
    
    if not voiceChannel:
        return await ctx.send("Bot is not in a voice channel.")
    if not currentlyPlaying:
        return await ctx.send("Bot is not playing anything.")
    currentlyPaused = False
    currentlyPlaying = False
    try:
        voiceChannel.stop()
        return await ctx.send("Stopped the currently playing song.")
    except Exception as e:
        print(e)
        return await ctx.send("Encountered an issue while trying to stop. Check bot logs.")
    
@bot.command()
async def disconnect(ctx:commands.context):
    global currentlyPlaying
    global currentlyListening
    global currentlyPaused
    global voiceChannel

    if not voiceChannel:
        return await ctx.send("Bot is not in a voice channel.")
    if currentlyPlaying:
        currentlyPlaying = False
        try:
            voiceChannel.stop()
        except Exception as e:
            print(e)
            return await ctx.send("Bot is detected as currently playing but encountered an error while stopping playing")
    try:
        await voiceChannel.disconnect()
        voiceChannel = None
        currentlyListening = False
        currentlyPaused = False
        currentlyPlaying = False





bot.run(TOKEN)