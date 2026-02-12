import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import wavelink
import asyncio

load_dotenv()

# ✅ Load Opus safely
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

    node = wavelink.Node(
        uri="127.0.0.1:2333",
        password="youshallnotpass"
    )

    await wavelink.NodePool.connect(client=bot, nodes=[node])

    lavalink_connected = True
    print("🎵 Lavalink connected successfully")


# ✅ MUSIC COMMAND (LAVALINK)
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

    print("Player:", vc)
    print("Connected:", vc.is_connected())
    print("Playing:", vc.is_playing())

    await ctx.send(f"🎶 Now playing: {track.title}")



# ✅ RAW DISCORD AUDIO TEST (NO LAVALINK)
@bot.command()
async def testvoice(ctx):
    if not ctx.author.voice:
        await ctx.send("Join a voice channel first 😤")
        return

    if ctx.voice_client:
        await ctx.voice_client.disconnect(force=True)
        await asyncio.sleep(1)

    vc = await ctx.author.voice.channel.connect()

    source = discord.FFmpegPCMAudio(
        executable=os.path.abspath("ffmpeg.exe"),
        source="anullsrc",  # 🔥 Generates silent audio internally
        before_options="-f lavfi",
        options="-t 5"
    )

    vc.play(source)

    await ctx.send("🎧 Testing voice transport...")


@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Stopped! 👋")


bot.run(os.getenv("DISCORD_TOKEN"))
