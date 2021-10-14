from discord.ext import commands
import discord
from datetime import datetime


class OwnerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.boot_time = datetime.now()
        self.version = 'v2.5.2'

    @commands.command(name='load', hidden=True)
    @commands.is_owner()
    async def load_cog(self, ctx, *, cog: str):
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
    async def unload_cog(self, ctx, *, cog: str):
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
    async def reload_cog(self, ctx, *, cog: str):
        """Command which Reloads a Module.
        Remember to use dot path. e.g: cogs.owner"""

        try:
            self.bot.reload_extension(f'cogs.{cog}')
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('**`SUCCESS`**')

    @commands.command(name='echo', hidden=True)
    @commands.is_owner()
    async def echo(self, ctx, message: str = None):
        print(ctx.message.content)
        if message is None:
            await ctx.send('echo echo echo echo...')
        else:
            await ctx.send(f'{message}')

    @commands.command(name='vme', hidden=True)
    @commands.is_owner()
    async def vme(self, ctx):
        time = datetime.now() - self.boot_time
        days = time.days
        hours, remainder = divmod(time.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        online_for = f'{days}:d {hours}:h {minutes}:m'
        embed = discord.Embed(colour=discord.Colour(0x50bdfe), description=f'Here is some information about me... \n '
                                                                           f'```'
                                                                           f'Version: {self.version}\n'
                                                                           f'Library: d.py rewrite \n'
                                                                           f'Uptime: {online_for} \n'
                                                                           f'Server Count: {len(self.bot.guilds)}\n'
                                                                           f'```')
        embed.set_footer(text='justin@sobieski.codes')
        await ctx.send(embed=embed)

    @commands.command(name='sts', hidden=True)
    @commands.is_owner()
    async def status(self, ctx, *, status: str = None):
        await self.bot.change_presence(status=discord.Status.idle, activity=discord.Game(f"{status}"))

    @commands.command(name='ui', hidden=True)
    @commands.is_owner()
    async def update_info(self, ctx, *, msg: str = None):
        if msg:
            self.bot.config['info'] = msg
            self.bot.config.save()
            await ctx.send('info has been updated.')
        else:
            await ctx.send('please provide a message.')


def setup(bot):
    bot.add_cog(OwnerCog(bot))
