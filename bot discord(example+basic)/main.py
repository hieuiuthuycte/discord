import os
import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

load_dotenv(os.path.join(BASE_DIR, ".env"))
TOKEN_BOT = os.getenv("TOKEN_BOT")

if not TOKEN_BOT:
    raise SystemExit("Không tìm thấy TOKEN_BOT trong file .env")

LOG_DIR = os.path.join(BASE_DIR, "log")
COMMANDS_DIR = os.path.join(BASE_DIR, "commands_py")
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(COMMANDS_DIR, exist_ok=True)

formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s", "%Y-%m-%d %H:%M:%S")


def make_file_handler(filename: str) -> logging.FileHandler:
    handler = logging.FileHandler(os.path.join(LOG_DIR, filename), encoding="utf-8")
    handler.setFormatter(formatter)
    return handler


bot_file = make_file_handler("bot.log")
chat_file = make_file_handler("chat.log")
console = logging.StreamHandler()
console.setFormatter(formatter)

bot_logger = logging.getLogger("bot")
bot_logger.setLevel(logging.INFO)
bot_logger.addHandler(bot_file)
bot_logger.addHandler(console)
bot_logger.propagate = False

chat_logger = logging.getLogger("chat")
chat_logger.setLevel(logging.INFO)
chat_logger.addHandler(chat_file)
chat_logger.addHandler(bot_file)
chat_logger.addHandler(console)
chat_logger.propagate = False


def clean(text: str) -> str:
    return text.replace("\r", "").replace("\n", " ⏎ ")


def describe_channel(channel) -> str:
    guild = getattr(channel, "guild", None)
    name = getattr(channel, "name", "DM")
    return f"{guild.name} #{name}" if guild else f"DM/{name}"


intents = discord.Intents.default()
intents.message_content = True
intents.messages = True


class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="", intents=intents, help_command=None)
        self.ready_logged = False

    async def setup_hook(self):
        for filename in sorted(os.listdir(COMMANDS_DIR)):
            if not filename.endswith(".py") or filename.startswith("_"):
                continue
            before = {cmd.name for cmd in self.commands}
            try:
                await self.load_extension(f"commands_py.{filename[:-3]}")
            except Exception as e:
                bot_logger.error(f"Lỗi khi load file lệnh {filename}: {e}")
                continue
            added = sorted({cmd.name for cmd in self.commands} - before)
            bot_logger.info(f"Đã load file lệnh: {filename} | lệnh: {', '.join(added) or 'không có'}")


bot = MyBot()


@bot.event
async def on_ready():
    if bot.ready_logged:
        return
    bot.ready_logged = True

    bot_logger.info(f"Bot đã đăng nhập: {bot.user} (ID: {bot.user.id})")
    names = sorted(cmd.name for cmd in bot.commands)
    bot_logger.info(f"Tổng số lệnh đã hoạt động ({len(names)}): {', '.join(names)}")
    for cmd in sorted(bot.commands, key=lambda c: c.name):
        bot_logger.info(f" - Lệnh định danh: {cmd.name} | {cmd.help or 'Không có mô tả'}")


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    content = clean(message.content) if message.content else ""
    if message.attachments:
        files = ", ".join(a.url for a in message.attachments)
        content += f" [file: {files}]"

    chat_logger.info(
        f"CHAT | {describe_channel(message.channel)} | "
        f"{message.author} ({message.author.id}) | {content}"
    )
    await bot.process_commands(message)


@bot.event
async def on_message_edit(before: discord.Message, after: discord.Message):
    if before.author.bot or before.content == after.content:
        return
    chat_logger.info(
        f"EDIT | {describe_channel(before.channel)} | "
        f"{before.author} ({before.author.id}) | "
        f"{clean(before.content)} -> {clean(after.content)}"
    )


@bot.event
async def on_raw_message_delete(payload: discord.RawMessageDeleteEvent):
    msg = payload.cached_message
    if msg is not None:
        if msg.author.bot:
            return
        content = clean(msg.content) if msg.content else ""
        if msg.attachments:
            content += " [file: " + ", ".join(a.url for a in msg.attachments) + "]"
        chat_logger.info(
            f"DELETE | {describe_channel(msg.channel)} | "
            f"{msg.author} ({msg.author.id}) | {content}"
        )
    else:
        chat_logger.info(
            f"DELETE | channel_id={payload.channel_id} | message_id={payload.message_id} | "
            f"(tin nhắn không có trong cache nên không có nội dung)"
        )


@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Thiếu tham số bắt buộc: `{error.param.name}`")
        return
    bot_logger.error(f"Lỗi lệnh {ctx.command}: {error}")
    await ctx.send("⚠️ Có lỗi xảy ra khi thực hiện lệnh này.")


if __name__ == "__main__":
    bot.run(TOKEN_BOT, log_handler=None)