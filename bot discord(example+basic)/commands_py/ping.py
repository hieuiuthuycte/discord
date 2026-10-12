from discord.ext import commands


class General(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="ping", description="Kiểm tra độ trễ của bot")
    async def ping(self, ctx: commands.Context):
        await ctx.send(f"Pong! {round(self.bot.latency * 1000)}ms")

    @commands.hybrid_command(name="say", description="Bot nói lại nội dung bạn nhập")
    async def say(self, ctx: commands.Context, *, text: str):
        await ctx.send(text)


async def setup(bot: commands.Bot):
    await bot.add_cog(General(bot))