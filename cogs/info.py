from discord.ext import commands


class info:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def info(self, ctx):
        await ctx.send(f"{self.bot.config.data.get('config').get('info')}")


def setup(bot):
    bot.add_cog(info(bot))
