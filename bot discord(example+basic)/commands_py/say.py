import discord
from discord.ext import commands

class Say(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="say", description="Bot nói lại nội dung bạn nhập")
    async def say(self, ctx: commands.Context, *, text: str):
        await ctx.send(text)

async def setup(bot):
    await bot.add_cog(Say(bot))
