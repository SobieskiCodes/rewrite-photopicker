from discord.ext import commands


def is_owner():
    def predictate(ctx):
        if ctx.author is ctx.guild.owner:
            return True
        return False
    return commands.check(predictate)


class GuildOwnerCog:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @is_owner()
    async def enable(self, ctx, cog: str=None):
        ''': Cogs are case senstive'''
        if not cog:
            cog_list = []
            for cog in self.bot.cogs:
                cog_list.append(cog)
            contains = ['OwnerCog', 'GuildOwnerCog']
            for x in contains:
                if x in cog_list:
                    cog_list.remove(x)

            await ctx.send(f'Available cogs are: {cog_list}')
            return

        if cog in (cog for cog in self.bot.cogs):
            self.bot.config.data['servers'][str(ctx.guild.id)][cog] = True
            self.bot.config.save()
            await ctx.send(f'{cog} Enabled.')
            return

        else:
            await ctx.send(f'I couldnt find a cog named {cog}')

    @commands.command()
    @is_owner()
    async def disable(self, ctx, cog: str = None):
        ''': Cogs are case senstive'''
        if not cog:
            cog_list = []
            for cog in self.bot.cogs:
                cog_list.append(cog)
            contains = ['OwnerCog', 'GuildOwnerCog']
            for x in contains:
                if x in cog_list:
                    cog_list.remove(x)
            await ctx.send(f'Available cogs are: {cog_list}')
            return

        if cog in self.bot.config.data.get('servers').get(str(ctx.guild.id)):
            self.bot.config.data['servers'][str(ctx.guild.id)].pop(cog, None)
            self.bot.config.save()
            await ctx.send(f'{cog} Disabled.')
            return

        else:
            await ctx.send(f'I couldnt find a cog named {cog}')

    @commands.command(aliases=['sp'])
    @is_owner()
    async def set_prefix(self, ctx, prefix: str=None):
        ''': Change the prefix of the bot, up to two chars.'''
        if not prefix:
            prefix = self.bot.config.data.get('servers').get(str(ctx.guild.id)).get('prefix')
            await ctx.send(f'current prefix is {prefix}')
            return
        else:
            if len(prefix) >= 3:
                await ctx.send('Prefix length too long.')
                return

            self.bot.config.data['servers'][str(ctx.guild.id)]['prefix'] = prefix
            self.bot.config.save()
            await ctx.send(f'Prefix updated to {prefix}')


def setup(bot):
    bot.add_cog(GuildOwnerCog(bot))
