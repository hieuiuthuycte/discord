import discord
from discord import app_commands
from discord.ext import commands

class BotCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    @app_commands.command(name="say", description="Bot nói lại nội dung bạn nhập")
    @app_commands.describe(text="Nội dung bạn muốn bot nói")
    async def say(self, interaction: discord.Interaction, text: str):
        await interaction.response.send_message(text)

async def setup(bot: commands.Bot):
    await bot.add_cog(BotCommands(bot))
