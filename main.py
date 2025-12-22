import discord
from discord.ext import commands
from datetime import datetime
import os
import yt_dlp
from keep_alive import keep_alive

# ===== INTENTS =====
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ===== MUSIC CONFIG =====
YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
}

FFMPEG_OPTIONS = {
    'options': '-vn'
}

DIGIMON_TEST = {
    "butterfly": "https://youtu.be/MuhkUzGAeHA",
    "braveheart": "https://youtu.be/bjQ_MIVLQcE",
    "breakup": "https://youtu.be/KH2j6dKPwxo"
}

# ===== BOT READY =====
@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Game(name="Giám sát khi con 🐒")
    )
    print(f"Bot đã online: {bot.user}")

# ===== AUTO REPLY =====
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    msg = message.content.lower()

    if msg in ["hello", "hi", "chào"]:
        await message.channel.send("👋 Chào bạn nha!")
    elif "bot đâu" in msg:
        await message.channel.send("🐵 Tao đây nè, gọi chi vậy?")
    elif msg == "ping":
        await message.channel.send("🏓 Pong!")

    await bot.process_commands(message)

# ===== LỆNH QUẢN LÝ =====
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)
    msg = await ctx.send(f"🧹 Đã xoá {amount} tin nhắn")
    await msg.delete(delay=3)

@clear.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Bạn không có quyền dùng lệnh này")

# ===== CHECK BOT =====
@bot.command()
async def checkbot(ctx):
    ping = round(bot.latency * 1000)
    time_now = datetime.now().strftime("%H:%M:%S")

    await ctx.send(
        f"🤖 **Bot đang hoạt động**\n"
        f"👤 Tên bot: `{bot.user}`\n"
        f"📶 Ping: `{ping}ms`\n"
        f"⏰ Thời gian: `{time_now}`"
    )

# ===== MUSIC COMMANDS =====
@bot.command()
async def join(ctx):
    if ctx.author.voice:
        await ctx.author.voice.channel.connect()
    else:
        await ctx.send("❌ Bạn chưa vào voice")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()

@bot.command()
async def play(ctx, song: str):
    if song not in DIGIMON_TEST:
        await ctx.send("❌ Chỉ test: butterfly / braveheart / breakup")
        return

    if not ctx.author.voice:
        await ctx.send("❌ Bạn chưa vào voice")
        return

    if not ctx.voice_client:
        await ctx.author.voice.channel.connect()

    url = DIGIMON_TEST[song]

    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)
        audio_url = info['url']

    ctx.voice_client.stop()
    ctx.voice_client.play(
        discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPTIONS)
    )

    await ctx.send(f"🎶 Đang phát: **{song.upper()}**")

# ===== START BOT =====
if __name__ == "__main__":
    keep_alive()  # Web server cho UptimeRobot

    TOKEN = os.getenv("DISCORD_TOKEN")
    if not TOKEN:
        raise RuntimeError("❌ Chưa set biến môi trường DISCORD_TOKEN")

    bot.run(TOKEN)
