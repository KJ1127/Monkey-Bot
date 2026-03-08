import discord
from discord.ext import commands
from datetime import datetime
import os
import time
from keep_alive import keep_alive
import traceback

# ===== INTENTS =====
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ===== BOT EVENTS =====
@bot.event
async def on_connect():
    print("🔌 Đã kết nối Gateway Discord")
    
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="Giám sát khỉ con 🐒"))
    server_count = len(bot.guilds)
    print(f"ai am sờ tiu ờ lai: {bot.user} | Servers: {server_count}")

    if server_count == 0:
        print("⚠️ Bot đang online nhưng chưa ở server nào. Hãy mời bot bằng OAuth2 URL (scope: bot, applications.commands).")
@bot.event
async def on_disconnect():
    print("⚠️ Bot bị ngắt kết nối Discord!")

@bot.event
async def on_resumed():
    print("🔄 Bot đã reconnect lại Discord!")

@bot.event
async def on_error(event, *args, **kwargs):
    print(f"❌ Lỗi trong event {event}")
    traceback.print_exc()

# ===== AUTO REPLY + GIF =====
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    msg = message.content.lower()

    # nếu ai ping bot
    if bot.user.mentioned_in(message):
        await message.channel.send(f"Moẹ đang mệt ping kẹc gì hả {message.author.mention}")

    if msg in ["hello", "hi", "chào"]:
        await message.channel.send("Chào kẹc gì mà chào,Quen biết gì nhau mà chào")

    elif "bot đâu" in msg:
        await message.channel.send("Đang lọ gọi con kẹc à")

    elif msg == "ping":
        await message.channel.send("🏓 Pong!")

    elif msg == "docchieu":
        await message.channel.send(
            "⚔️ **ĐỘC CHIÊU!**",
            file=discord.File("gif/docchieu.gif")
        )

    await bot.process_commands(message)

# ===== MUSIC FILE MAP =====
DIGIMON_MUSIC = {
    "butterfly": "music/butterfly.mp3",
    "braveheart": "music/braveheart.mp3",
    "breakup": "music/breakup.mp3"
}

FFMPEG_OPTIONS = {
    "options": "-vn -filter:a volume=0.6"
}

# ===== VOICE COMMANDS =====
@bot.command()
async def join(ctx):
    if not ctx.author.voice:
        await ctx.send("❌ Bạn chưa vào voice")
        return

    if ctx.voice_client:
        if ctx.voice_client.channel == ctx.author.voice.channel:
            await ctx.send("✅ Bot đã ở sẵn trong voice này rồi")
            return

        await ctx.voice_client.move_to(ctx.author.voice.channel)
        await ctx.send("🔄 Bot đã chuyển sang voice của bạn")
        return

    await ctx.author.voice.channel.connect()


@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()

@bot.command()
async def play(ctx, song: str):
    song = song.lower()

    if song not in DIGIMON_MUSIC:
        await ctx.send("❌ Chỉ có: butterfly / braveheart / breakup")
        return

    if not ctx.author.voice:
        await ctx.send("❌ Bạn chưa vào voice")
        return

    if not ctx.voice_client:
        await ctx.author.voice.channel.connect()
    elif ctx.voice_client.channel != ctx.author.voice.channel:
        await ctx.send("❌ Bạn cần vào cùng voice với bot để phát nhạc")
        return

    def after_playing(error):
        if error:
            print("❌ Lỗi phát nhạc:", error)

    source = discord.FFmpegPCMAudio(
        DIGIMON_MUSIC[song],
        **FFMPEG_OPTIONS
    )

    ctx.voice_client.stop()
    ctx.voice_client.play(source, after=after_playing)

    await ctx.send(f"🎶 Đang phát: **{song.upper()}**")

# ===== CLEAR CHAT =====
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):

    if amount > 100:
        await ctx.send("❌ Tối đa chỉ được xóa 100 tin để tránh rate limit!")
        return

    await ctx.channel.purge(limit=amount + 1)
    msg = await ctx.send(f"🧹 Đã xóa {amount} tin nhắn")
    await msg.delete(delay=3)

@clear.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Bạn không có quyền dùng lệnh này")
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return

    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Bạn thiếu tham số cho lệnh này")
        return

    if isinstance(error, commands.BadArgument):
        await ctx.send("❌ Tham số không hợp lệ")
        return

    print(f"❌ Command error: {error}")

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

# ===== START BOT (AUTO RESTART IF CRASH) =====
if __name__ == "__main__":
    keep_alive()

    TOKEN = (os.getenv("DISCORD_TOKEN") or "").strip()
    if not TOKEN:
        raise RuntimeError("❌ Chưa set biến môi trường DISCORD_TOKEN")

    print("Đang khởi động bot....")

    while True:
        try:
            bot.run(TOKEN)
            break
        except discord.LoginFailure:
            raise RuntimeError("❌ DISCORD_TOKEN không hợp lệ hoặc đã hết hạn")
        except discord.PrivilegedIntentsRequired:
            raise RuntimeError(
                "❌ Bot đang bật intents đặc quyền trong code nhưng chưa bật trong Discord Developer Portal"
            )
        except KeyboardInterrupt:
            print("⏹️ Đã dừng bot theo yêu cầu người dùng")
            break
        except Exception as exc:
            print(f"⚠️ Mất kết nối Discord hoặc lỗi tạm thời: {exc}")
            print("🔁 Sẽ thử kết nối lại sau 15 giây...")
            time.sleep(15)

