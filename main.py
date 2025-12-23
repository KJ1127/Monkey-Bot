import discord
from discord.ext import commands
from datetime import datetime
import os
from keep_alive import keep_alive

# ===== INTENTS =====
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ===== BOT READY =====
@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Game(name="Giám sát khỉ con 🐒")
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
        await message.channel.send("🐒 Tao đây nè, gọi chi vậy?")

    elif msg == "ping":
        await message.channel.send("🏓 Pong!")

    await bot.process_commands(message)

# ===== LỆNH QUẢN LÝ =====
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)
    msg = await ctx.send(f"🧹 Đã xóa {amount} tin nhắn")
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
        f"✅ **Bot đang hoạt động!**\n"
        f"🤖 Tên bot: `{bot.user}`\n"
        f"⏱️ Ping: `{ping}ms`\n"
        f"🕒 Thời gian: `{time_now}`"
    )

# =================================================
# ============ PHẦN PHÁT NHẠC FILE =================
# =================================================

MUSIC_FILES = {
    "butterfly": "music/butterfly.mp3",
    "braveheart": "music/braveheart.mp3",
    "breakup": "music/breakup.mp3"
}

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
    song = song.lower()

    if song not in MUSIC_FILES:
        await ctx.send("❌ Chỉ có: butterfly / braveheart / breakup")
        return

    if not ctx.author.voice:
        await ctx.send("❌ Bạn chưa vào voice")
        return

    if not ctx.voice_client:
        await ctx.author.voice.channel.connect()

    file_path = MUSIC_FILES[song]

    if not os.path.isfile(file_path):
        await ctx.send("❌ Không tìm thấy file nhạc")
        return

    ctx.voice_client.stop()
    ctx.voice_client.play(
        discord.FFmpegPCMAudio(file_path)
    )

    await ctx.send(f"🎶 Đang phát: **{song.upper()}**")

# ===== START BOT =====
if __name__ == "__main__":
    keep_alive()  # Web server cho UptimeRobot (có cũng được, không có vẫn chạy)

    TOKEN = os.getenv("DISCORD_TOKEN")
    if not TOKEN:
        raise RuntimeError("❌ Chưa set biến môi trường DISCORD_TOKEN")

    bot.run(TOKEN)
