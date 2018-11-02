from discord.ext import commands
import os
from cogs.util import pyson
import asyncio
class info:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def info(self, ctx):
        '''info - see current information you might need to know about changes.
        '''
        await ctx.send(f"{self.bot.config.data.get('config').get('info')}")

    @commands.command()
    async def fill(self, ctx):
        for server in self.bot.guilds:
            if not os.path.exists(f"./data/servers/{str(server.id)}/config.json"):
                try:
                    os.makedirs(f"./data/servers/{str(server.id)}/")
                    open(f'./data/servers/{str(server.id)}/config.json', 'a').close()
                    self.bot.serverconfig = pyson.Pyson(f'data/servers/{str(server.id)}/config.json')
                    self.bot.serverconfig.data = {"albums": {}, "config": {"admins": [], "prefix": "."}}
                    self.bot.serverconfig.save()
                    print('going')
                    await asyncio.sleep(1)
                except OSError as e:
                    if e.errno != e.errno.EEXIST:
                        raise


def setup(bot):
    bot.add_cog(info(bot))
