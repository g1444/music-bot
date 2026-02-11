import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import wavelink
import asyncio

load_dotenv()

# Load opus DLL with full path
if not discord.opus.is_loaded():
    try:
        discord.opus.load_opus('G:/codes/discord/music bot/opus.dll')
    except:
        pass

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

lavalink_connected = False

@bot.event
async def on_ready():
    global lavalink_connected
    if lavalink_connected:
        return

    print(f"✅ Logged in as {bot.user}")

    node = wavelink.Node(
        uri="http://127.0.0.1:2333",
        password="youshallnotpass"
    )

    await wavelink.NodePool.connect(
        client=bot,
        nodes=[node]
    )

    lavalink_connected = True
    print("🎵 Lavalink connected successfully")

@bot.event
async def on_wavelink_track_start(player: wavelink.Player, track: wavelink.tracks):
    print(f"🎵 Track STARTED: {track.title}")

@bot.event  
async def on_wavelink_track_end(player: wavelink.Player, track: wavelink.tracks, reason):
    print(f"⏹️ Track ENDED: {track.title} | Reason: {reason}")

@bot.command()
async def play(ctx, *, search: str):
    if not ctx.author.voice:
        await ctx.send("Join a voice channel first 😤")
        return

    # Always disconnect and reconnect fresh
    if ctx.voice_client:
        await ctx.voice_client.disconnect(force=True)
        await asyncio.sleep(1)

    vc = await ctx.author.voice.channel.connect(cls=wavelink.Player)
    await asyncio.sleep(2)  # Give it time to establish connection

    tracks = await wavelink.YouTubeTrack.search(search)
    if not tracks:
        await ctx.send("No results found 😐")
        return

    track = tracks[0]
    
    # Play BEFORE setting volume
    await vc.play(track)
    await asyncio.sleep(0.5)
    await vc.set_volume(200)  # Try higher volume

    await ctx.send(f"🎶 Now playing: **{track.title}**")

    print("▶ is_playing:", vc.is_playing())
    print("🔊 volume:", vc.volume)
    print("🎵 Current track:", vc.current)

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Stopped!")

bot.run(os.getenv("DISCORD_TOKEN"))