import discord
from discord.ext import commands


class Hello(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="hello", description="Chào bot")
    async def hello(self, ctx: commands.Context):
        await ctx.send(f"👋 Xin chào {ctx.author.mention}!")


async def setup(bot):
    await bot.add_cog(Hello(bot))