from discord.ext import commands
import discord
from cogs.util import pyson

def is_guild_owner():
    def predictate(ctx):
        if ctx.author is ctx.guild.owner:
            return True
        return False
    return commands.check(predictate)


class GuildOwnerCog:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['sp'])
    @is_guild_owner()
    async def setprefix(self, ctx, prefix: str=None):
        ''': Change the prefix of the bot, up to two chars.'''
        if not prefix:
            self.bot.serverconfig = pyson.Pyson(f'data/servers/{str(ctx.guild.id)}/config.json')
            prefix = self.bot.serverconfig .data.get('config').get('prefix')
            await ctx.send(f'current prefix is {prefix}')
            return
        else:
            if len(prefix) >= 3:
                await ctx.send('Prefix length too long.')
                return

            self.bot.config.data['servers'][str(ctx.guild.id)]['prefix'] = prefix
            self.bot.config.save()
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
