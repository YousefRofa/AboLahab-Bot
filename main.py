import discord
from discord.utils import get
import datetime
import youtube_dl
import os
import re
import asyncio
import random
import time

TOKEN = ""
intents = discord.Intents().default()
intents.members = True

client = discord.Client(intents=intents)
game_roles = {"valorant": "<@&858019403169267712>",
              "gta": "<@&851423984583311370>",
              "minecraft": "<@&851410979967336459>",
              "rocket league": "<@&851424045756186644>",
              "call of duty": "<@&851410664173600798>",
              "fortnite": "<@&851410897036771348>",
              "fifa": "<@&851410949910298664>"}
game_reactions = {"857943441656250381": "valorant",
                  "858028059478196294": "rocket league",
                  "858028068608933938": "gta",
                  "858028088936103966": "fortnite",
                  "858024587401232424": "minecraft",
                  "858028078927839272": "call of duty",
                  }
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
ydl_opts = {
    'format': 'bestaudio/best',
}
member_role = 851663193218875433
VC_role = 933011782811918406
time_window_milliseconds = 5000
max_msg_per_window = 4
over_max_msg_per_window = 6
author_msg_times = {}

songs = []
current_song = ''
current_song_num = 0
songMsg = []
channels_Sticks = {}


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name="rofa"))
    print("abo lahab is ready as {0.user}".format(client))


@client.event
async def on_thread_join(thread):
    await thread.join()


@client.event
async def on_member_join(member):
    guild = client.get_guild(729300120897716275)
    channel = guild.get_channel(851393543364673536)
    embed = discord.Embed.from_dict(eval("""{'color': 5111808, 'type': 'rich', 'description': 'To verify, go to <#851660522717053007>'
    'and read the rules carefully and react to them. This will give you access to the rest of the server.\\n\\nNext go to <#851412433805377558> and pick the games you play !!'
    '\\n\\nIf you have any issues do DM <@!481932096986939403> or <@!729267290503381052> and we will help you out.'
    '\\n\\nYou can enjoy messing with <@!974401140466782219> and have fun :)'
    '\\n\\n**NOTE: If you do not verify you will not be able to access the server.**', 'title': 'Welcome to the server!'}"""))
    await channel.send(content=member.mention, embed=embed)


@client.event
async def on_raw_reaction_add(reaction):
    global reactionroles, current_song_num
    current_song_num = int(current_song_num)
    guild = client.get_guild(729300120897716275)
    memberrole = get(guild.roles, id=member_role)
    channel = client.get_channel(reaction.channel_id)
    msg = await channel.fetch_message(reaction.message_id)
    if reaction.channel_id == 851660522717053007:
        await reaction.member.add_roles(memberrole)

    if reaction.channel_id == 851412433805377558:
        game_name = game_reactions.get(str(reaction.emoji.id))
        role_id = game_roles.get(game_name)[3:-1]
        role = get(guild.roles, id=int(role_id))
        await reaction.member.add_roles(role)

    if reaction.channel_id == 871747768522248272 and msg.author.id == 974401140466782219 and reaction.user_id != 974401140466782219:
        guild = client.get_guild(729300120897716275)
        voice = discord.utils.get(client.voice_clients, guild=guild)
        if str(reaction.emoji) == '⏯':
            user = client.get_user(reaction.user_id)
            await msg.remove_reaction(str(reaction.emoji), user)
            if voice.is_playing():
                voice.pause()
            else:
                voice.resume()
        elif str(reaction.emoji) == '🔁':
            user = client.get_user(reaction.user_id)
            await msg.remove_reaction(str(reaction.emoji), user)
            if voice.is_playing():
                voice.pause()
            else:
                voice.resume()
            current_song_num -= 1
            await editSongsMsg()
            playNext(client)
        elif str(reaction.emoji) == '▶':
            user = client.get_user(reaction.user_id)
            await msg.remove_reaction(str(reaction.emoji), user)
            if not current_song_num > len(songs):
                if voice.is_playing():
                    voice.pause()
                await editSongsMsg()
                playNext(client)
        elif str(reaction.emoji) == '◀':
            user = client.get_user(reaction.user_id)
            await msg.remove_reaction(str(reaction.emoji), user)
            if not current_song_num < 1:
                if voice.is_playing():
                    voice.pause()
                current_song_num -= 2
                await editSongsMsg()
                playNext(client)


@client.event
async def on_raw_reaction_remove(reaction):
    global reactionroles
    guild = client.get_guild(729300120897716275)
    memberrole = get(guild.roles, id=member_role)
    channel = client.get_channel(reaction.channel_id)
    msg = await channel.fetch_message(reaction.message_id)
    if reaction.channel_id == 851660522717053007:
        member = discord.utils.get(msg.guild.members, id=reaction.user_id)
        await member.remove_roles(memberrole)

    if reaction.channel_id == 851412433805377558:
        game_name = game_reactions.get(str(reaction.emoji.id))
        role_id = game_roles.get(game_name)[3:-1]
        role = get(guild.roles, id=int(role_id))
        member = discord.utils.get(msg.guild.members, id=reaction.user_id)
        await member.remove_roles(role)


async def editSongsMsg():
    global songMsg, current_song_num
    embed = discord.Embed.from_dict(eval("{" + f"'color': 5111808, 'type': 'rich',"
                                               "'description': '**Songs list**\\n'}"))
    if len(str(current_song_num)) == 1:
        current_song_num = "0" + str(current_song_num)
    for song_num in range(len(songs)):
        if song_num == int(current_song_num):
            songs_names = "**" + str(songs[song_num].get('title', None) + "**" + "\n")
            embed.add_field(name=f"**{song_num + 1}/**", value=f"{songs_names}", inline=True)
        else:
            songs_names = str(songs[song_num].get('title', None) + "\n")
            embed.add_field(name=f"{song_num + 1}/ ", value=f"{songs_names}", inline=True)
    await songMsg[-1].edit(embed=embed)


async def sendSongsMsg(channel):
    global songMsg
    embed = discord.Embed.from_dict(eval("{" + f"'color': 5111808, 'type': 'rich',"
                                               "'description': '**Songs list**\\n'}"))
    global current_song_num
    if len(str(current_song_num)) == 1:
        current_song_num = "0" + str(current_song_num)
    for song_num in range(len(songs)):
        if song_num == int(current_song_num):
            songs_names = "**" + str(songs[song_num].get('title', None) + "**" + "\n")
            embed.add_field(name=f"**{song_num + 1}/**", value=f"{songs_names}", inline=True)
        else:
            songs_names = str(songs[song_num].get('title', None) + "\n")
            embed.add_field(name=f"{song_num + 1}/ ", value=f"{songs_names}", inline=True)

    song_msg = await channel.send(embed=embed)
    songMsg.append(song_msg)
    for i in ['◀', '⏯', '🔁', '▶']:
        await song_msg.add_reaction(i)


def playNext(client):
    global current_song, current_song_num
    guild = client.get_guild(729300120897716275)
    voice = discord.utils.get(client.voice_clients, guild=guild)
    current_song = discord.FFmpegPCMAudio(songs[int(current_song_num)]['formats'][0]['url'], **FFMPEG_OPTIONS)
    current_song_num = int(current_song_num) + 1
    voice.play(current_song, after=lambda e: playNext(client))


async def play_music(client, message):
    global current_song, current_song_num
    guild = client.get_guild(729300120897716275)
    voice = discord.utils.get(client.voice_clients, guild=guild)
    if message != "":
        try:
            url = re.search("(?P<url>https?://[^\s]+)", str(message.content)).group("url")
            await message.channel.send("la7za 34an soty ray7")
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if 'entries' in info:
                    # Can be a playlist or a list of videos
                    video = info['entries']

                    # loops entries to grab each video_url
                    for i, item in enumerate(video):
                        video = info['entries'][i]
                        songs.append(video)
                else:
                    songs.append(info)
                if not voice.is_playing():
                    current_song = discord.FFmpegPCMAudio(songs[current_song_num]['formats'][0]['url'],
                                                          **FFMPEG_OPTIONS)
                    await sendSongsMsg(message.channel)
                    current_song_num += 1
                    voice.play(current_song, after=lambda e: playNext(client))
                else:
                    await sendSongsMsg(message.channel)
        except Exception as e:
            print(e)
            await message.channel.send("m4 lama td5lni call el 2wl ya ahbl")
    else:
        try:
            if not voice.is_playing():
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(songs[current_song_num], download=False)
                    current_song = discord.FFmpegPCMAudio(info['formats'][0]['url'], **FFMPEG_OPTIONS)
                    current_song_num += 1
                    await voice.play(current_song, after=lambda e: playNext(client))
        except:
            pass


@client.event
async def on_message(message):
    global author_msg_counts, current_song, channels_Sticks
    guild = client.get_guild(729300120897716275)
    bot_channel = guild.get_channel(974652633732235265)
    if message.author == client.user:
        return

    if message.reference is not None:
        msg = await message.channel.fetch_message(message.reference.message_id)
        msg_id = msg.author.id
    else:
        msg_id = 0
    if msg_id == 974401140466782219 or 'abo lahab' in message.content.lower() or 'abolahab' in message.content.lower() or '<@974401140466782219>' in message.content.lower():
        guild = client.get_guild(729300120897716275)
        voice = discord.utils.get(client.voice_clients, guild=guild)
        if message.content.lower().startswith("play"):
            playing = str(message.content)
            for i in ['abo lahab', 'abolahab', '<@974401140466782219>', 'play']:
                try:
                    playing = playing.lower().replace(i.lower(), '')
                except:
                    pass
            await client.change_presence(activity=discord.Game(name=str(playing)))
            await message.channel.send("7ader")
        elif "call" in message.content.lower():
            if voice:
                await voice.disconnect()
            await message.channel.send("24tato")
            await message.author.voice.channel.connect()
        elif "etl3" in message.content.lower() or "2tl3" in message.content.lower():
            if not voice:
                await message.channel.send("ma ana m4 fe call 2sln")
            else:
                await message.channel.send("24tato")
                await voice.disconnect()
        elif "kamel" in message.content.lower() or "kml" in message.content.lower() or "kaml" in message.content.lower() or "resume" in message.content.lower():
            guild = client.get_guild(729300120897716275)
            voice = discord.utils.get(client.voice_clients, guild=guild)
            voice.resume()
            await message.channel.send("24tato")
        elif "4a8al" in message.content.lower():
            await play_music(client, message)

    if message.content.lower().startswith("stick"):
        stick_content = message.content[5:]
        channels_Sticks[message.channel] = [stick_content]
        await message.channel.send("Channel sticked !")

    if message.content.lower().startswith("unstick"):
        for channel in channels_Sticks.keys():
            if message.channel == channel:
                channels_Sticks.pop(channel)
                await message.channel.send("Channel unsticked !")
                break

    for channel in channels_Sticks.keys():
        if message.channel == channel:
            if len(channels_Sticks.get(channel)) == 2:
                await channels_Sticks[channel][1].delete()
            else:
                channels_Sticks[channel].append("")
            sticky_message = await channel.send(channels_Sticks.get(channel)[0])
            channels_Sticks[channel][1] = sticky_message
        message.channel.send("Message sticked in this channel !")

    if message.content.lower().startswith("a") and len(message.content) > 1:
        if message.content[1] == "1":
            await message.channel.send(
                "Rule A1 : No blank nicknames, no inappropriate nicknames and no sexually explicit nicknames.")
        elif message.content[1] == "2":
            await message.channel.send("Rule A2 : No blank profile pictures and no inappropriate profile pictures.")
        elif message.content[1] == "3":
            await message.channel.send(
                "Rule A3 :  Moderators reserve the right to change nicknames and reserve the right to use their own discretion regardless of any rule..")
        elif message.content[1] == "4":
            await message.channel.send("Rule A4:  No inviting bots.")
        elif message.content[1] == "5":
            await message.channel.send("Rule A5:  No bugs, exploits, glitches, hacks, bugs, etc.")
        elif message.content[1] == "6":
            await message.channel.send("Rule A6:  Rules apply to DMing other members of the server.")
    elif message.content.lower().startswith("b"):
        if message.content[1] == "1":
            await message.channel.send(
                "Rule B1 :  No annoying, loud or high pitch noises and reduce the amount of background noise, if possible.")
        elif message.content[1] == "2":
            await message.channel.send(
                "Rule B2 : Moderators reserve the right to disconnect you from a voice channel if your sound quality is poo abd reserve the right to disconnect, mute, deafen, or move members to and from voice channels.")
    elif message.content.lower().startswith("c"):
        if message.content[1] == "1":
            await message.channel.send("Rule C1 : No commands spam.")
        elif message.content[1] == "2":
            await message.channel.send("Rule C2 :  No playing music except in the music room.")

    if message.content.lower().startswith(
            "ya abo lahab") or message.content.lower() == "<@974401140466782219>" or message.content.lower() == "abolahab" \
            or message.content.lower() == "abo lahab":
        replies = ["5eer", "na3am", "na3ameen", "ha?", "eh yasta"]
        await message.channel.send(random.choice(replies))

    if "jhonny sins" in message.content.lower():
        await message.channel.send(
            "https://tenor.com/view/johnny-sins-erik-dal%C4%B1-sins-erik-dal%C4%B1-erik-dance-gif-16064270")

    if "happy dance" in message.content.lower():
        await message.channel.send("https://tenor.com/view/cute-cat-kitten-excited-dance-gif-23200050")

    for word in ["السلام", "el7", "alsalam", "mawlay", "mwlay", "elhamdullah", "eslam", "alhamdullah", "الله اكبر"]:
        if word in message.content.lower():
            await message.channel.send("MAWLAAAAAAAAAAAAAAAAAAAAAAAAAAAAY")

    if 'siu' in message.content.lower() or 'sui' in message.content.lower():
        await message.channel.send(
            "https://tenor.com/view/siu-ronaldo-siu-cristiano-cristiano-ronaldo-siu-meme-gif-24574747")
    if message.content.startswith("$"):
        embed = discord.Embed.from_dict(eval("{'color': 5111808, 'type': 'rich','description': '" + str(
            message.author) + "\\n\\n hwa elly 2al :    " + message.content[1:] +
                                             " \\n\\n fe " + str(f"<#{message.channel.id}>") + "'}"))
        await bot_channel.send(embed=embed)
        await message.channel.send(message.content[1:])
        await message.delete()

    for game in game_roles.keys():
        if message.content.lower().startswith(f"{game}?") or message.content.lower().startswith(f"{game} ?"):
            await message.channel.send(f"Yalla ya 4bab {game_roles.get(game)}")

    author_id = message.author.id
    curr_time = datetime.datetime.now().timestamp() * 1000

    # Make empty list for author id, if it does not exist
    if not author_msg_times.get(author_id, False):
        author_msg_times[author_id] = []

    # Append the time of this message to the users list of message times
    author_msg_times[author_id].append(curr_time)

    # Find the beginning of our time window.
    expr_time = curr_time - time_window_milliseconds

    # Find message times which occurred before the start of our window
    expired_msgs = [
        msg_time for msg_time in author_msg_times[author_id]
        if msg_time < expr_time
    ]

    # Remove all the expired messages times from our list
    for msg_time in expired_msgs:
        author_msg_times[author_id].remove(msg_time)
    # ^ note: we probably need to use a mutex here. Multiple threads

    if len(author_msg_times[author_id]) > over_max_msg_per_window:
        await message.channel.send(f"MA 2OLNA KFAYA SODA3 YA <@{author_id}>")
    elif len(author_msg_times[author_id]) > max_msg_per_window:
        await message.channel.send(f"mkfaya sda3 baa ya <@{author_id}>")


@client.event
async def on_voice_state_update(member, before, after):
    guild = client.get_guild(729300120897716275)
    vc_role = get(guild.roles, id=VC_role)
    if before.channel is None and after.channel:
        await member.add_roles(vc_role)
    elif after.channel is None:
        await member.remove_roles(vc_role)


client.run(TOKEN)

