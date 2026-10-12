import os
import logging
import sys
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN_BOT = os.getenv("TOKEN_BOT")

if not TOKEN_BOT:
    raise SystemExit("Không tìm thấy TOKEN_BOT trong file .env")

LOG_DIR = "log"
os.makedirs(LOG_DIR, exist_ok=True)

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

bot = commands.Bot(command_prefix=[], intents=intents, help_command=None)

@bot.event
async def on_ready():
    bot_logger.info(f"Bot đã đăng nhập: {bot.user} (ID: {bot.user.id})")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)

    target_folder = "comands_py"
    folder_path = os.path.join(current_dir, target_folder)

    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            if filename.endswith(".py") and not filename.startswith("_"):
                cog_name = filename[:-3]
                try:
                    await bot.load_extension(f"{target_folder}.{cog_name}")
                    bot_logger.info(f"Đã nạp thành công cog: {cog_name}")
                except Exception as e:
                    bot_logger.error(f"Lỗi khi nạp file {filename}: {e}")
    else:
        bot_logger.error(f"Không tìm thấy thư mục {target_folder} tại {folder_path}")

    try:
        synced = await bot.tree.sync()
        bot_logger.info(f"Đã đồng bộ thành công {len(synced)} lệnh Slash Commands lên Discord")
    except Exception as e:
        bot_logger.error(f"Lỗi khi đồng bộ Slash Commands: {e}")

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

@bot.event
async def on_message_edit(before: discord.Message, after: discord.Message):
    if before.author.bot or before.content == after.content:
        return
    chat_logger.info(
        f"EDIT | {describe_channel(before.channel)} | "
        f"{before.author} ({before.author.id}) | "
        f"'{clean(before.content)}' -> '{clean(after.content)}'"
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
            f"DELETE | channel_id={payload.channel_id} | message_id={payload.message_id} "
            f"| (tin nhắn không có trong cache nên không có nội dung)"
        )

if __name__ == "__main__":
    bot.run(TOKEN_BOT, log_handler=None)
