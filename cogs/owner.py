from discord.ext import commands
import discord
from datetime import datetime


class OwnerCog:

    def __init__(self, bot):
        self.bot = bot
        self.boottime = datetime.now()
        self.version = 'v1.0.0'

    @commands.command(name='load', hidden=True)
    @commands.is_owner()
    async def cog_load(self, ctx, *, cog: str):
        """Command which Loads a Module.
        Remember to use dot path. e.g: cogs.owner"""

        try:
            self.bot.load_extension(f'cogs.{cog}')
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('**`SUCCESS`**')

    @commands.command(name='unload', hidden=True)
    @commands.is_owner()
    async def cog_unload(self, ctx, *, cog: str):
        """Command which Unloads a Module.
        Remember to use dot path. e.g: cogs.owner"""

        try:
            self.bot.unload_extension(f'cogs.{cog}')
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('**`SUCCESS`**')

    @commands.command(name='reload', hidden=True)
    @commands.is_owner()
    async def cog_reload(self, ctx, *, cog: str):
        """Command which Reloads a Module.
        Remember to use dot path. e.g: cogs.owner"""

        try:
            self.bot.unload_extension(f'cogs.{cog}')
            self.bot.load_extension(f'cogs.{cog}')
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('**`SUCCESS`**')

    @commands.command(name='cogenable', hidden=True)
    @commands.is_owner()
    async def cog_enable(self, ctx, server: str=None, cog: str=None):
        if not server or not cog:
            await ctx.send('You forgot the server or cog nub.')
            return
        if not server.isdigit():
            await ctx.send('thats not even a valid server, what are you doing...')
            return
        if server not in self.bot.config.data.get('servers'):
            await ctx.send(f'couldnt find server "{server}"')
            return
        if cog not in self.bot.cogs:
            await ctx.send(f'{cog} doesnt seem like a real cog my man')
            return
        else:
            if cog not in self.bot.config.data.get('servers').get(server):
                self.bot.config.data['servers'][server][cog] = True
                self.bot.config.save()
                await ctx.send(f'{cog} enabled for server: {server}.')
                return
            else:
                await ctx.send(f'{cog} is already enabled for server: {server}')

    @commands.command(name='cogdisable', hidden=True)
    @commands.is_owner()
    async def cog_disable(self, ctx, server: str=None, cog: str=None):
        if not server or not cog:
            await ctx.send('You forgot the server or cog nub.')
            return
        if not server.isdigit():
            await ctx.send('thats not even a valid server, what are you doing...')
            return
        if server not in self.bot.config.data.get('servers'):
            await ctx.send(f'couldnt find server "{server}"')
            return
        if cog not in self.bot.cogs:
            await ctx.send(f'{cog} doesnt seem like a real cog my man')
            return
        else:
            if cog in self.bot.config.data.get('servers').get(server):
                self.bot.config.data['servers'][server].pop(cog, None)
                self.bot.config.save()
                await ctx.send(f'{cog} disabled for server: {server}.')
                return
            else:
                await ctx.send(f'{cog} i dont see that cog enabled for server: {server}')

    @commands.command(name='echo', hidden=True)
    @commands.is_owner()
    #add support for server/channel blah blah blah.
    async def echo(self, ctx, message: str=None):
        print(ctx.message.content)
        if message is None:
            await ctx.send('echo echo echo echo...')
        else:
            await ctx.send(f'{message}')

    @commands.command(name='vme', hidden=True)
    @commands.is_owner()
    async def vme(self, ctx):
        time = datetime.now() - self.boottime
        days = time.days
        hours, remainder = divmod(time.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        onlinefor = f'{days}:d {hours}:h {minutes}:m'
        embed = discord.Embed(colour=discord.Colour(0x50bdfe), description=f'Here is some information about me... \n '
                                                                           f'```'
                                                                           f'Version: {self.version}\n'
                                                                           f'Library: d.py rewrite \n'
                                                                           f'Uptime: {onlinefor} \n'
                                                                           f'Server Count: {len(self.bot.guilds) - 2}\n'
                                                                           f'Member Count: {len(self.bot.users)}'
                                                                           f'```')
        embed.set_footer(text='justin@sobieski.codes')
        await ctx.send(embed=embed)

    @commands.command(name='inv', hidden=True)
    @commands.is_owner()
    async def invite(self, ctx):
        embed = discord.Embed(colour=discord.Colour(0x608f30),
                              description=f'Invite me [here](https://discordapp.com/oauth2/authorize?client_id'
                                          f'={self.bot.user.id}&scope=bot&permissions=0)')
        embed.set_footer(text='')
        await ctx.send(embed=embed)

    @commands.command(name='sts', hidden=True)
    @commands.is_owner()
    async def status(self, ctx, status: str=None):
        await self.bot.change_presence(status=discord.Status.idle, activity=discord.Game(f"{status}"))


def setup(bot):
    bot.add_cog(OwnerCog(bot))
