import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import wavelink
import asyncio

load_dotenv()

# ✅ Opus (optional but safe)
try:
    discord.opus.load_opus(os.path.abspath("opus.dll"))
except Exception as e:
    print("Opus load error:", e)

print("Opus loaded:", discord.opus.is_loaded())

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

lavalink_connected = False

@bot.event
async def on_ready():
    global lavalink_connected
    if lavalink_connected:
        return

    print(f"✅ Logged in as {bot.user}")

    # 🔥 PUBLIC LAVALINK NODE
    node = wavelink.Node(
        uri="lavalink.serenetia.com:443",
        password="https://dsc.gg/ajidevserver",
        secure=True
    )

    await wavelink.NodePool.connect(client=bot, nodes=[node])

    lavalink_connected = True
    print("🎵 Public Lavalink connected successfully")


@bot.command()
async def play(ctx, *, search: str):
    if not ctx.author.voice:
        await ctx.send("Join VC 😤")
        return

    vc: wavelink.Player = ctx.voice_client

    if not vc:
        vc = await ctx.author.voice.channel.connect(cls=wavelink.Player)

    await asyncio.sleep(1)

    tracks = await wavelink.YouTubeTrack.search(search)
    if not tracks:
        await ctx.send("No results 😑")
        return

    track = tracks[0]

    await vc.set_volume(150)
    await vc.play(track)

    print("Connected:", vc.is_connected())
    print("Playing:", vc.is_playing())

    await ctx.send(f"🎶 Now playing: {track.title}")
@bot.command()
async def playlist(ctx, url: str):
    if not ctx.author.voice:
        await ctx.send("Join VC first 😤")
        return

    vc: wavelink.Player = ctx.voice_client
    if not vc:
        vc = await ctx.author.voice.channel.connect(cls=wavelink.Player)

    await ctx.send("Reading playlist… ⏳")

    result = await wavelink.YouTubeTrack.search(url)

    if not result:
        await ctx.send("Failed to load playlist 😑")
        return

    # ✅ THIS is the missing logic
    if hasattr(result, "tracks"):
        tracks = result.tracks
    else:
        tracks = result

    count = 0
    for track in tracks:
        await vc.queue.put_wait(track)
        count += 1

    await ctx.send(f"Queued {count} tracks 😏")

    if not vc.is_playing():
        await vc.play(await vc.queue.get_wait())

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Stopped! 👋")


bot.run(os.getenv("DISCORD_TOKEN"))