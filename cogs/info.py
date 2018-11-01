from discord.ext import commands
import discord


class info:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def info(self, ctx):
        await ctx.send(f"{self.bot.config.data.get('config').get('info')}")

    @commands.command()
    async def test(self, ctx):
        print(ctx.author.guild_permissions.manage_guild)


def setup(bot):
    bot.add_cog(info(bot))
