from discord.ext import commands


class info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def info(self, ctx):
        """
        info - see current information you might need to know about changes.
        """
        await ctx.send(f"{self.bot.config.get('info')}")


def setup(bot):
    bot.add_cog(info(bot))
