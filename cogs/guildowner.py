from discord.ext import commands
import discord
from cogs.util.checks import is_guild_owner


class GuildOwnerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['sp'])
    @is_guild_owner()
    async def setprefix(self, ctx, prefix: str=None):
        """: Change the prefix of the bot, up to two chars."""
        if not prefix:
            prefix_list = await self.bot.get_prefix(ctx.message)
            await ctx.send(f'`{"` and `".join(prefix_list[1:])}` are my two current prefixes.')
            return
        else:
            if len(prefix) >= 3:
                await ctx.send('Prefix length too long.')
                return
            await self.bot.db.execute(f"REPLACE INTO GuildConfig(ID, Prefix) VALUES (?, ?)", (ctx.guild.id, prefix))
            await self.bot.db.commit()
            await ctx.send(f'Prefix updated to {prefix}')

    @commands.command(name='inv', hidden=True)
    @is_guild_owner()
    async def invite(self, ctx):
        embed = discord.Embed(colour=discord.Colour(0x608f30),
                              description=f'Invite me [here](https://discordapp.com/oauth2/authorize?client_id'
                                          f'={self.bot.user.id}&scope=bot&permissions=0)')
        embed.set_footer(text='')
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(GuildOwnerCog(bot))
