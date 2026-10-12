import discord
from discord import app_commands
from discord.ext import commands

from comands_py.say import BotCommands

class helloCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    @app_commands.command(name="hello", description="Chào bot")
    async def hello(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Xin chào {interaction.user.mention}!")
async def setup(bot: commands.Bot):
    await bot.add_cog(helloCommands(bot)) 